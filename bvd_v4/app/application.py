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
    CheckResponse,
    SearchRequest,
    SearchResponse,
)

app = Flask(__name__)

sentry_url = os.environ.get("SENTRY_URL")
if sentry_url:
    sentry = Sentry(app, logging=True, level=logging.ERROR, dsn=sentry_url)
else:
    logging.warning("SENTRY_URL not provided")


@app.route("/health")
def health():
    return jsonify("success")


def get_bvd_id(client, country, bvd_id, company_number):
    if bvd_id is not None:
        return bvd_id
    result = client.search(company_number=company_number, country=country,)
    if result.data:
        return result.data[0].bvd_id
    else:
        return None


@app.route("/registry-check", methods=["POST"])
@request_model(RegistryCheckRequest)
def registry_check(request):
    # Assuming we always have either a BvD ID or a company number

    client = Client(request.credentials.key)

    bvd_id = get_bvd_id(
        client,
        request.input_data.country_of_incorporation,
        request.input_data.bvd_id,
        request.input_data.number,
    )

    if bvd_id:
        search_results = client.fetch_data(bvd_id)
    else:
        search_results = None

    if search_results:
        data = CompanyData.from_bvd(search_results.data[0])
    else:
        data = {}

    return jsonify(
        CheckResponse(
            {
                "output_data": data,
                "errors": client.errors,
                "raw": client.raw_responses,
                "price": 0,  # TODO: can we remove this?
            }
        ).to_primitive()
    )


@app.route("/ownership-check", methods=["POST"])
def ownership_check():
    abort(501)


@app.route("/search", methods=["POST"])
@request_model(SearchRequest)
def company_search(request):
    client = Client(request.credentials.key)
    search_results = client.search(
        request.input_data.name,
        request.input_data.country,
        state=request.input_data.state,
        company_number=request.input_data.number,
    )
    return jsonify(
        SearchResponse({
            "output_data": [
                Candidate.from_bvd(hit)
                for hit in sorted(
                    search_results.data,
                    reverse=True,
                    key=lambda hit: hit.match.zero.score,
                )
            ] if search_results else [],
            "errors": client.errors,
            "raw": client.raw_responses,
        }).to_primitive()
    )