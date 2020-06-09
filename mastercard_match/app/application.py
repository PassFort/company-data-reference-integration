import logging
import os
import traceback

import requests

from flask import Flask, Response, jsonify, request
from raven.contrib.flask import Sentry
from requests.exceptions import ConnectionError, Timeout
from werkzeug.exceptions import HTTPException
from json import JSONDecodeError

from .api.errors import Error, ErrorCode, MatchException
from .api.match import Merchant, TerminationInquiryRequest
from .api.passfort import InquiryRequest, RetroInquiryRequest, RetroInquiryDetailsRequest, validate_model
from .auth.oauth import OAuth, load_signing_key
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


@app.after_request
def send_analytics(response):
    tags = [
        'method:{}'.format(request.method),
        'endpoint:{}'.format(request.endpoint),
        'path:{}'.format(request.path),
        'full_path:{}'.format(request.full_path),
        'status_code:{}'.format(response.status_code)
    ]
    app.dd.increment('passfort.services.match.api_call', tags=tags)
    return response


@app.route('/inquiry-request', methods=['POST'])
@validate_model(InquiryRequest)
def inquiry_request(data: InquiryRequest):
    return MatchHandler(
        data.credentials.certificate,
        data.credentials.consumer_key,
        data.config.use_sandbox,
    ).inquiry_request(data)


@app.route('/retro-inquiry', methods=['POST'])
@validate_model(RetroInquiryRequest)
def retro_inquiry(data: RetroInquiryRequest):
    return MatchHandler(
        data.credentials.certificate,
        data.credentials.consumer_key,
    ).retro_inquiry_request(data.credentials.acquirer_id)


@app.route('/retro-inquiry-details', methods=['POST'])
@validate_model(RetroInquiryDetailsRequest)
def retro_inquiry_details(data: RetroInquiryDetailsRequest):
    return MatchHandler(
        data.credentials.certificate,
        data.credentials.consumer_key,
    ).retro_inquiry_details_request(data, data.credentials.acquirer_id, data.ref)


@app.errorhandler(400)
def api_400(error):
    logging.error(error.description)
    return jsonify(errors=[error.description]), 400


@app.errorhandler(MatchException)
def app_error(check_error):
    response = check_error.response
    try:
        response_content = response.json()
        errors = response_content.get('Errors')
        errors = errors.get('Error') if errors else []

        if isinstance(errors, list):
            errors = [e.get('Description') for e in errors]
        else:
            errors = [errors.get('Description')]
    # Sometimes they send back xml :|
    except JSONDecodeError:
        response_content = response.text
        errors = [response_content]

    if response.status_code == 400:
        errors = [Error.provider_unknown_error(e) for e in errors]
        return jsonify(
            raw=response_content,
            errors=errors
        ), 200
    elif response.status_code == 401 or response.status_code == 403:
        errors = [Error.provider_misconfiguration_error(e) for e in errors]
        return jsonify(
            raw=response_content,
            errors=errors
        ), 200
    else:
        errors = [Error.provider_unknown_error(e) for e in errors]
        return jsonify(
            raw=response_content,
            errors=errors
        ), 500


@app.errorhandler(ConnectionError)
def connection_error(e):
    logging.error(traceback.format_exc())
    return jsonify(errors=[Error.provider_connection_error(e)]), 200


@app.errorhandler(Timeout)
def timeout_error(e):
    logging.error(traceback.format_exc())
    return jsonify(errors=[Error.provider_connection_error(e)]), 200
