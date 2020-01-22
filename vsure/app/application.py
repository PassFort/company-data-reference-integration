import logging
import os
import traceback
from flask import Flask, jsonify, abort
from raven.contrib.flask import Sentry
from werkzeug.exceptions import HTTPException

import app.json_logger
from .api.input_types import validate_model, VisaCheckRequest
from .api.errors import VSureServiceException, Error
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
    logging.error(error.description)
    return jsonify(errors=[error.description]), 400


@app.errorhandler(VSureServiceException)
def api_provider_error(error):
    if error.message in {'Error: Invalid key', 'Error: Key is required'}:
        return jsonify(errors=[Error.provider_misconfiguration_error(error.message)], raw=error.raw_output), 500
    else:
        return jsonify(errors=[Error.provider_unknown_error(error)], raw=error.raw_output), 500


@app.errorhandler(Exception)
def handle_exceptions(error):
    logging.error(traceback.format_exc())
    code = 500
    if isinstance(error, HTTPException):
        code = error.code
    return jsonify(errors=[Error.from_exception(error)]), code
