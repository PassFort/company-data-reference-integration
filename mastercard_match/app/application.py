import os
import logging
from flask import Flask, jsonify
from raven.contrib.flask import Sentry
import traceback
from werkzeug.exceptions import HTTPException
from .auth.oauth import OAuth, load_signing_key
import requests
from .api.passfort import validate_model, InquiryRequest
from .api.match import TerminationInquiryRequest, Merchant
from .request_handler import MatchHandler


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


@app.route('/health')
def health():
    return jsonify('success')


@app.route('/inquiry-request')
@validate_model(InquiryRequest)
def inquiry_request(data: InquiryRequest):
    handler = MatchHandler(data.credentials.certificate, data.credentials.consumer_key)
    return handler.inquiry_request(data, 0, 10)


@app.errorhandler(400)
def api_400(error):
    logging.error(error.description)
    return jsonify(errors=[error.description]), 400
