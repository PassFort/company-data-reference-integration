import os
import logging
import traceback
from flask import Flask, jsonify
from raven.contrib.flask import Sentry

from .api.types import validate_model, ScreeningRequest, Error
from .request_handler import search_request


app = Flask(__name__)
logging.getLogger().setLevel(logging.INFO)


class DataDogWrapper:
    def __init__(self, mock=True):
        self.mock = mock

    def increment(self, metric, value=1, tags=None, sample_rate=1):
        from datadog import statsd

        if self.mock:
            logging.info('Increment {} called with value {} and tags: {}'.format(metric, value, tags))
        else:
            try:
                statsd.increment(metric, value, tags, sample_rate)
            except Exception:
                logging.error('Statsd error when increment {} was '
                              'called with value {} and tags: {}'.format(metric, value, tags))


def initialize_datadog():
    from datadog import initialize

    try:
        initialize(statsd_host=os.environ['STATSD_HOST_IP'],
                   statsd_port=os.environ['STATSD_HOST_PORT'])
        return DataDogWrapper(mock=False)
    except Exception:
        return DataDogWrapper(mock=True)


app.dd = initialize_datadog()


sentry_url = os.environ.get('SENTRY_URL')
if sentry_url:
    sentry = Sentry(
        app,
        logging=True,
        level=logging.ERROR, dsn=sentry_url
    )


@app.after_request
def send_analytics(response):
    from flask import request
    tags = [
        'method:{}'.format(request.method),
        'endpoint:{}'.format(request.endpoint),
        'path:{}'.format(request.path),
        'full_path:{}'.format(request.full_path),
        'status_code:{}'.format(response.status_code)
    ]
    app.dd.increment('passfort.services.comply_advantage.api_call', tags=tags)
    return response


@app.route('/health')
def health():
    return jsonify('success')


@app.route('/screening_request', methods=['POST'])
@validate_model(ScreeningRequest)
def screen_request(request_data: ScreeningRequest):

    return jsonify(search_request(
        request_data.input_data,
        request_data.config,
        request_data.credentials,
        request_data.is_demo
    ))


@app.errorhandler(400)
def api_400(error):
    return jsonify(errors=[error.description]), 400


@app.errorhandler(500)
def api_500(error):
    logging.error(traceback.format_exc())
    return jsonify(errors=[Error.from_exception(error)]), 500
