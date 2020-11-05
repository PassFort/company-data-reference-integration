import asyncio
import logging
import os
import time
from functools import wraps

from flask import Flask, jsonify, abort
from raven.contrib.flask import Sentry

from app.validation import request_model
from app.bvd.datasets import DataSet
from app.bvd.client import Client as BvDClient
from app.passfort.client import Client as PassFortClient
from app.passfort.company_data import CompanyData, CompanyDataCheckResponse
from app.bvd.types import SearchResult
from app.passfort.types import (
    AddToPortfolioRequest,
    Candidate,
    CreatePortfolioRequest,
    MonitoringEventsRequest,
    Portfolio,
    RegistryCheckRequest,
    RegistryEvent,
    ShareholdersEvent,
    SearchRequest,
    SearchResponse,
    OfficersEvent,
)

logging.getLogger().setLevel(logging.INFO)

app = Flask(__name__)

sentry_url = os.environ.get("SENTRY_URL")
if sentry_url:
    sentry = Sentry(app, logging=True, level=logging.ERROR, dsn=sentry_url)
else:
    logging.warning("SENTRY_URL not provided")


class DataDogWrapper:
    def __init__(self, mock=True):
        self.mock = mock

    def increment(self, metric, value=1, tags=None, sample_rate=1):
        from datadog import statsd

        if self.mock:
            logging.info('Increment {} called with value {} and tags: {}'.format(metric, value, tags))
        else:
            try:
                statsd.increment(metric, value, tags, sample_rate)
            except Exception:
                logging.error('Statsd error when increment {} was '
                              'called with value {} and tags: {}'.format(metric, value, tags))

    def histogram(self, metric, value, tags=None, sample_rate=1):
        from datadog import statsd

        if self.mock:
            logging.info('Histogram {} called with value {} and tags: {}'.format(metric, value, tags))
        try:
            statsd.histogram(metric, value, tags, sample_rate)
        except Exception:
            logging.error('Statsd error when histogram {} was '
                          'called with value {} and tags: {}'.format(metric, value, tags))

    def track_time(self, metric):
        def track_time_decorator(fn):
            @wraps(fn)
            def wrapped_fn(*args, **kwargs):
                start = time.time()
                try:
                    result = fn(*args, **kwargs)
                except Exception as e:
                    self.histogram(metric + '.error', time.time() - start)
                    raise e

                self.histogram(metric, time.time() - start)
                return result

            return wrapped_fn

        return track_time_decorator


def initialize_datadog():
    from datadog import initialize

    try:
        initialize(statsd_host=os.environ['STATSD_HOST_IP'],
                   statsd_port=os.environ['STATSD_HOST_PORT'])
        return DataDogWrapper(mock=False)
    except Exception:
        return DataDogWrapper(mock=True)


app.dd = initialize_datadog()

    
@app.route("/health")
def health():
    return jsonify("success")


def get_bvd_id(client, country, bvd_id, company_number, name, state):
    if bvd_id is not None:
        return bvd_id
    result = client.search(
        company_number=company_number, country=country, name=name, state=state
    )
    hits = result.sorted_hits() if result else []
    if hits:
        return hits[0].bvd_id
    else:
        return None


@app.route("/company-data-check", methods=["POST"])
@app.dd.track_time("passfort.services.bvd_v4.report")
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


@app.route("/search", methods=["POST"])
@app.dd.track_time("passfort.services.bvd_v4.search")
@request_model(SearchRequest)
def company_search(request):
    client = BvDClient(request.credentials.key, request.is_demo)

    if request.input_data.name == request.input_data.number:
        input_data = request.input_data
        name_results = client.search(
            name=input_data.name,
            country=input_data.country,
            state=input_data.state,
        )
        number_results = client.search(
            company_number=input_data.number,
            country=input_data.country,
            state=input_data.state,
        )
        hits = SearchResult.merged_hits(name_results, number_results)
    else:
        search_results = client.search(
            request.input_data.name,
            country=request.input_data.country,
            state=request.input_data.state,
            company_number=request.input_data.number,
        )
        hits = search_results.sorted_hits() if search_results else []

    return jsonify(
        SearchResponse(
            {
                "output_data": [
                    Candidate.from_bvd(hit)
                    for hit
                    in hits
                ],
                "errors": client.errors,
                "raw": client.raw_responses,
            }
        ).to_primitive()
    )


@app.route("/monitoring_portfolio", methods=["POST"])
@app.dd.track_time("passfort.services.bvd_v4.monitoring_portfolio")
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
@app.dd.track_time("passfort.services.bvd_v4.monitoring")
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
@app.dd.track_time("passfort.services.bvd_v4.monitoring_events")
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
