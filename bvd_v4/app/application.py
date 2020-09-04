import os
import logging

from flask import Flask, jsonify, request, abort
from raven.contrib.flask import Sentry

from app.bvd.client import Client
from app.passfort.types import CompanyData

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
    # TODO: read from input and search if not present
    bvd_id = "US310958666"

    search_results = Client(request.credentials.key).fetch_data(bvd_id)
    if search_results.data:
        for match in search_results.data:
            return jsonify(CompanyData.from_bvd(match).to_primitive())
    else:
        abort(404, "no results found")


@app.route('/ownership-check', methods=['POST'])
def ownership_check():
    abort(501)


@app.route('/search', methods=['POST'])
def company_search():
    abort(501)
