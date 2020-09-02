import os
import logging
import traceback

from flask import Flask, request, jsonify
from raven.contrib.flask import Sentry
from requests.exceptions import ConnectionError, Timeout
from app.api import routes
from app.api.error import Error


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


def create_app():
    app = Flask(__name__)

    logging.getLogger().setLevel(logging.INFO)

    sentry_url = os.environ.get('SENTRY_URL')
    if sentry_url:
        sentry = Sentry(
            app,
            logging=True,
            level=logging.ERROR, dsn=sentry_url
        )

    app.dd = initialize_datadog()
    routes.init_app(app)

    @app.after_request
    def send_analytics(response):
        tags = [
            'method:{}'.format(request.method),
            'endpoint:{}'.format(request.endpoint),
            'path:{}'.format(request.path),
            'full_path:{}'.format(request.full_path),
            'status_code:{}'.format(response.status_code)
        ]
        app.dd.increment('passfort.services.loqate.api_call', tags=tags)
        return response

    @app.errorhandler(Timeout)
    def timeout_error(error):
        logging.error(traceback.format_exc())
        return jsonify(errors=[Error.provider_connection_error(error)]), 200

    @app.errorhandler(ConnectionError)
    def connection_error(error):
        logging.error(traceback.format_exc())
        return jsonify(errors=[Error.provider_connection_error(error)]), 200

    return app
