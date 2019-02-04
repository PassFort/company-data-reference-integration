import os
import logging
from flask import Flask, jsonify
from raven.contrib.flask import Sentry
import app.json_logger
from app.api.types import validate_model, EKYCRequest, Error
from .request_handler import ekyc_request, EquifaxProviderError, EquifaxConnectionError

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


@app.route('/ekyc-check', methods=['POST'])
@validate_model(EKYCRequest)
def run_ekyc_check(request_data):
    return jsonify(ekyc_request(request_data))


@app.errorhandler(400)
def api_400(error):
    return jsonify(errors=[error.description]), 400


@app.errorhandler(EquifaxProviderError)
def api_provider_error(error):
    return jsonify(errors=[Error.provider_unknown_error(error)]), 500
