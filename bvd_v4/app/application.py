import os
import logging

from flask import Flask, jsonify, abort
from raven.contrib.flask import Sentry

from app.validation import request_model
from app.bvd.datasets import DataSet
from app.bvd.client import Client as BvDClient
from app.passfort.client import Client as PassFortClient
from app.passfort.company_data import CompanyData, CompanyDataCheckResponse
from app.passfort.types import (
    AddToPortfolioRequest,
    Candidate,
    CreatePortfolioRequest,
    MonitoringEventsRequest,
    OwnershipCheckRequest,
    OwnershipCheckResponse,
    OwnershipCompanyData,
    Portfolio,
    RegistryCheckRequest,
    RegistryCheckResponse,
    RegistryCompanyData,
    RegistryEvent,
    SearchRequest,
    SearchResponse,
    ShareholdersEvent,
    OfficersEvent,
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


def get_bvd_id(client, country, bvd_id, company_number, name, state):
    if bvd_id is not None:
        return bvd_id
    result = client.search(
        company_number=company_number, country=country, name=name, state=state
    )
    hits = result.sorted_hits()
    if hits:
        return hits[0].bvd_id
    else:
        return None


@app.route("/company-data-check", methods=["POST"])
@request_model(RegistryCheckRequest)
def company_data_check(request):
    # Assuming we always have either a BvD ID or a company number

    client = BvDClient(request.credentials.key, request.is_demo)

    bvd_id = get_bvd_id(
        client,
        request.input_data.country_of_incorporation,
        request.input_data.bvd_id,
        request.input_data.number,
        request.input_data.name,
        request.input_data.state_of_incorporation,
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
            {"output_data": data, "errors": client.errors, "raw": client.raw_responses}
        ).to_primitive()
    )


@app.route("/registry-check", methods=["POST"])
@request_model(RegistryCheckRequest)
def registry_check(request):
    # Assuming we always have either a BvD ID or a company number

    client = BvDClient(request.credentials.key, request.is_demo)

    bvd_id = get_bvd_id(
        client,
        request.input_data.country_of_incorporation,
        request.input_data.bvd_id,
        request.input_data.number,
        request.input_data.name,
        request.input_data.state_of_incorporation,
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
    client = BvDClient(request.credentials.key, request.is_demo)

    bvd_id = get_bvd_id(
        client,
        request.input_data.country_of_incorporation,
        request.input_data.bvd_id,
        request.input_data.number,
        request.input_data.name,
        request.input_data.state_of_incorporation,
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
    client = BvDClient(request.credentials.key, request.is_demo)
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
                    Candidate.from_bvd(hit) for hit in search_results.sorted_hits()
                ]
                if search_results
                else [],
                "errors": client.errors,
                "raw": client.raw_responses,
            }
        ).to_primitive()
    )


@app.route("/monitoring_portfolio", methods=["POST"])
@request_model(CreatePortfolioRequest)
def create_monitoring_portfolio(request):
    client = BvDClient(request.credentials.key, request.is_demo)
    result = client.create_record_set(request.input_data.name)
    return jsonify(
        {
            "output_data": Portfolio(
                {"id": result.id, "count": result.count}
            ).to_primitive(),
            "errors": client.errors,
            "raw": client.raw_responses,
        }
    )


@app.route("/monitoring", methods=["POST"])
@request_model(AddToPortfolioRequest)
def add_to_monitoring_portfolio(request):
    client = BvDClient(request.credentials.key, request.is_demo)
    result = client.add_to_record_set(
        request.input_data.portfolio_id, request.input_data.bvd_id,
    )
    return jsonify(
        {
            "output_data": Portfolio(
                {"id": result.id, "count": result.count,}
            ).to_primitive(),
            "errors": client.errors,
            "raw": client.raw_responses,
        }
    )


@app.route("/monitoring_events", methods=["POST"])
@request_model(MonitoringEventsRequest)
def get_monitoring_events(request):
    bvd_client = BvDClient(request.credentials.key, request.is_demo)
    passfort_client = PassFortClient(request.input_data.callback_url)

    registry_result = bvd_client.fetch_registry_updates(
        request.input_data.portfolio_id,
        request.input_data.timeframe.from_,
        request.input_data.timeframe.to,
    )
    ownership_result = bvd_client.fetch_ownership_updates(
        request.input_data.portfolio_id,
        request.input_data.timeframe.from_,
        request.input_data.timeframe.to,
    )
    officers_result = bvd_client.fetch_officers_updates(
        request.input_data.portfolio_id,
        request.input_data.timeframe.from_,
        request.input_data.timeframe.to,
    )

    events = (
        [RegistryEvent.from_bvd_update(update) for update in registry_result.data]
        + [
            ShareholdersEvent.from_bvd_update(update)
            for update in ownership_result.data
        ]
        + [OfficersEvent.from_bvd_update(update) for update in officers_result.data]
    )

    passfort_client.send_events(
        request.input_data.portfolio_id,
        request.input_data.portfolio_name,
        request.input_data.timeframe.to,
        events,
        bvd_client.raw_responses,
    )

    return jsonify({"errors": bvd_client.errors, "raw": bvd_client.raw_responses,})
