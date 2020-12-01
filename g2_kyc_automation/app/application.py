import logging
import os
import time
from functools import wraps

from flask import Flask, jsonify, abort
from raven.contrib.flask import Sentry
from app.types import ScreeningRequest, PollRequest
from app.api_client import ApiClient
from app.validation import request_model

logging.getLogger().setLevel(logging.INFO)

app = Flask(__name__)

sentry_url = os.environ.get("SENTRY_URL")
if sentry_url:
    sentry = Sentry(app, logging=True, level=logging.ERROR, dsn=sentry_url)
else:
    logging.warning("SENTRY_URL not provided")


@app.route("/health")
def health():
    return jsonify("success")


@app.route("/screening_request", methods=['POST'])
@request_model(ScreeningRequest)
def screening_request(screening_request: ScreeningRequest):
    client = ApiClient(**screening_request.client_setup)
    case_id, errors, raw = client.create_report(screening_request)

    return {"output_data": case_id, "errors": errors, "raw": raw}


@app.route("/poll_report", methods=['POST'])
@request_model(PollRequest)
def poll_report(poll_request: PollRequest):
    client = ApiClient(**poll_request.client_setup)

    report_is_ready, errors, raw = client.poll_report(poll_request)

    response = jsonify({'errors': errors, "raw": raw})
    if report_is_ready:
        return response
    else:
        response.status_code = 202
        return response


@app.route("/report", methods=['POST'])
def report():
    abort(501)
