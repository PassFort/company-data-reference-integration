import os
import logging

from flask import Flask, jsonify, abort
from raven.contrib.flask import Sentry

from app.validation import request_model
from app.bvd.datasets import DataSet
from app.bvd.client import Client
from app.passfort.company_data import CompanyData, CompanyDataCheckResponse
from app.passfort.types import (
    Candidate,
    RegistryCheckRequest,
    RegistryCheckResponse,
    RegistryCompanyData,
    OwnershipCheckRequest,
    OwnershipCheckResponse,
    OwnershipCompanyData,
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


@app.route("/company-data-check", methods=["POST"])
@request_model(RegistryCheckRequest)
def company_data_check(request):
    # Assuming we always have either a BvD ID or a company number

    client = Client(request.credentials.key, request.is_demo,)

    bvd_id = get_bvd_id(
        client,
        request.input_data.country_of_incorporation,
        request.input_data.bvd_id,
        request.input_data.number,
    )

    if bvd_id:
        search_results = client.fetch_company_data(bvd_id)
    else:
        search_results = None

    if search_results and search_results.data:
        data = CompanyData.from_bvd(search_results.data[0])
    else:
        data = {}

    return jsonify(
        CompanyDataCheckResponse(
            {"output_data": data, "errors": client.errors, "raw": client.raw_responses,}
        ).to_primitive()
    )


@app.route("/registry-check", methods=["POST"])
@request_model(RegistryCheckRequest)
def registry_check(request):
    # Assuming we always have either a BvD ID or a company number

    client = Client(request.credentials.key, request.is_demo,)

    bvd_id = get_bvd_id(
        client,
        request.input_data.country_of_incorporation,
        request.input_data.bvd_id,
        request.input_data.number,
    )

    if bvd_id:
        search_results = client.fetch_registry_data(bvd_id)
    else:
        search_results = None

    if search_results and search_results.data:
        data = RegistryCompanyData.from_bvd(search_results.data[0])
    else:
        data = {}

    return jsonify(
        RegistryCheckResponse(
            {
                "output_data": data,
                "errors": client.errors,
                "raw": client.raw_responses,
                "price": 0,  # TODO: can we remove this?
            }
        ).to_primitive()
    )


@app.route("/ownership-check", methods=["POST"])
@request_model(OwnershipCheckRequest)
def ownership_check(request):
    client = Client(request.credentials.key, request.is_demo,)

    bvd_id = get_bvd_id(
        client,
        request.input_data.country_of_incorporation,
        request.input_data.bvd_id,
        request.input_data.number,
    )

    if bvd_id:
        search_results = client.fetch_ownership_data(bvd_id)
    else:
        search_results = None

    if search_results and search_results.data:
        data = OwnershipCompanyData.from_bvd(search_results.data[0])
    else:
        data = {}

    return jsonify(
        OwnershipCheckResponse(
            {
                "output_data": data,
                "errors": client.errors,
                "raw": client.raw_responses,
                "price": 0,  # TODO: can we remove this?
            }
        ).to_primitive()
    )


@app.route("/search", methods=["POST"])
@request_model(SearchRequest)
def company_search(request):
    client = Client(request.credentials.key, request.is_demo,)
    search_results = client.search(
        request.input_data.name,
        country=request.input_data.country,
        state=request.input_data.state,
        company_number=request.input_data.number,
    )
    return jsonify(
        SearchResponse(
            {
                "output_data": [
                    Candidate.from_bvd(hit)
                    for hit in sorted(
                        search_results.data,
                        reverse=True,
                        key=lambda hit: hit.match.zero.score,
                    )
                ]
                if search_results
                else [],
                "errors": client.errors,
                "raw": client.raw_responses,
            }
        ).to_primitive()
    )
