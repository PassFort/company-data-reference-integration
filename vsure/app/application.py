from flask import Flask, jsonify
import logging
import os
from raven.contrib.flask import Sentry

import app.json_logger
from .api.input_types import validate_model, VisaCheckRequest
from .api.errors import VSureServiceException, Error, InputDataException
from .request_handler import visa_request, vsure_request

app = Flask(__name__)

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


@app.route('/visa-check', methods=["POST"])
@validate_model(VisaCheckRequest)
def run_visa_check(request_data):
    return jsonify(vsure_request(request_data))


@app.errorhandler(400)
def api_400(error):
    return jsonify(errors=[error.description]), 400

@app.errorhandler(500)
def api_500(error):
    return jsonify(errors=[error.description]), 500

@app.errorhandler(VSureServiceException)
def api_provider_error(error):
    return jsonify(errors=[Error.provider_unknown_error(error)], raw=error.raw_output), 500


@app.errorhandler(InputDataException)
def api_provider_error(error):
    return jsonify(errors=[Error.bad_api_request(error)], raw=error.raw_output), 500