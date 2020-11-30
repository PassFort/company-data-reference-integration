import logging
import os
import time
from functools import wraps

from flask import Flask, jsonify, abort
from raven.contrib.flask import Sentry

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
def screening_request():
    abort(501)


@app.route("/poll_report", methods=['POST'])
def poll_report():
    abort(501)


@app.route("/report", methods=['POST'])
def report():
    abort(501)
