from flask import Flask, jsonify
import logging
import os
from raven.contrib.flask import Sentry

from .api.types import validate_model, VisaCheckRequest
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
