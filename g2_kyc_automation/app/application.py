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
    client = ApiClient(
        screening_request.credentials.client_id,
        screening_request.credentials.client_secret,
        use_sandbox=screening_request.config.use_sandbox,
        is_demo=screening_request.is_demo,
    )
    return client.get_auth_token()


@app.route("/poll_report", methods=['POST'])
def poll_report():
    abort(501)


@app.route("/report", methods=['POST'])
def report():
    abort(501)
