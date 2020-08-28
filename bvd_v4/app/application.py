import os
import logging

from flask import Flask, jsonify, request, abort
from raven.contrib.flask import Sentry

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


@app.route('/registry-check', methods=['POST'])
def registry_check():
    abort(501)


@app.route('/ownership-check', methods=['POST'])
def ownership_check():
    abort(501)


@app.route('/search', methods=['POST'])
def company_search():
    abort(501)
