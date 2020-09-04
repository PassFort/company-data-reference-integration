import os
import logging

from flask import Flask, jsonify, abort
from raven.contrib.flask import Sentry

from app.validation import request_model
from app.bvd.client import Client
from app.passfort.types import (
    Candidate,
    CompanyData,
    RegistryCheckRequest,
    SearchRequest,
    SearchResponse,
)

app = Flask(__name__)

sentry_url = os.environ.get("SENTRY_URL")
if sentry_url:
    sentry = Sentry(app, logging=True, level=logging.ERROR, dsn=sentry_url)


@app.route("/health")
def health():
    return jsonify("success")


@app.route("/registry-check", methods=["POST"])
@request_model(RegistryCheckRequest)
def registry_check(request):
    # TODO: read from input and search if not present
    bvd_id = "US310958666"

    search_results = Client(request.credentials.key).fetch_data(bvd_id)
    if search_results.data:
        for match in search_results.data:
            return jsonify(CompanyData.from_bvd(match).to_primitive())
    else:
        abort(404, "no results found")


@app.route("/ownership-check", methods=["POST"])
def ownership_check():
    abort(501)


@app.route("/search", methods=["POST"])
@request_model(SearchRequest)
def company_search(request):
    search_results = Client(request.credentials.key).search(
        request.input_data.name, request.input_data.country,
    )

    response = SearchResponse({"output_data": [
        Candidate.from_bvd(hit)
        for hit
        in sorted(search_results.data, reverse=True, key=lambda hit: hit.match.zero.score)
    ], "errors": []})

    return jsonify(response.to_primitive())
