import json
import os
import re

from dataclasses import dataclass
from typing import Optional, List, Tuple

from flask import Flask, send_file, request, abort, Response

from app.api import (
    Address,
    CommercialRelationshipType,
    Charge,
    DemoResultType,
    Error,
    ErrorType,
    Field,
    RunCheckResponse,
    RunCheckRequest,
    SearchRequest,
    SearchResponse,
    validate_models,
)
from app.http_signature import HTTPSignatureAuth
from app.startup import integration_key_store

# If `entrypoint` is not defined in app.yaml, App Engine will look for an app
# called `app` in `main.py`.
app = Flask(__name__)

auth = HTTPSignatureAuth()

SUPPORTED_COUNTRIES = ['GBR', 'USA', 'CAN', 'NLD']


@dataclass
class CheckInput:
    country_of_incorporation: str

@dataclass
class SearchInput:
    country_of_incorporation: str


@app.before_request
def pre_request_logging():
    request_data = '\n' + request.data.decode('utf8')
    request_data = request_data.replace('\n', '\n    ')

    app.logger.info(f'{request.method} {request.url}{request_data}')


@app.after_request
def post_request_logging(response):
    if response.direct_passthrough:
        response_data = '\n(direct pass-through)'
    else:
        response_data = '\n' + response.data.decode('utf8')
    response_data = response_data.replace('\n', '\n    ')

    app.logger.info(f'{response.status} {request.url}{response_data}')
    return response


@auth.resolve_key
def resolve_key(key_id):
    return integration_key_store.get(key_id)


@app.route('/')
def index():
    return send_file('../static/metadata.json', cache_timeout=-1)


@app.route('/config')
@auth.login_required
def get_config():
    return send_file('../static/config.json', cache_timeout=-1)



def _try_load_demo_result(response_model, commercial_relationship: CommercialRelationshipType, name: str):

    def _sanitize_filename(value: str, program=re.compile('^[a-zA-Z_]+$')):
        if not program.match(value):
            abort(Response('Invalid demo request'), status=400)
        return value

    import logging
    filename = f'../static/demo_results/{_sanitize_filename(name)}.json'
    logging.info(filename)
    try:
        # Load file relative to current script
        with open(os.path.join(os.path.dirname(__file__), filename), 'r') as file:
            demo_response = response_model().import_data(
                json.load(file), apply_defaults=True)
    except FileNotFoundError:
        return None

    if commercial_relationship == CommercialRelationshipType.PASSFORT:
        demo_response.charges = [
            Charge({
                'amount': 100,
                'reference': 'DUMMY REFERENCE'
            }),
            Charge({
                'amount': 50,
                'sku': 'NORMAL'
            })
        ]

    return demo_response


def _run_demo_check(
    check_input: CheckInput,
    demo_result: str,
    commercial_relationship: CommercialRelationshipType
) -> RunCheckResponse:
    country = check_input.country_of_incorporation

    if demo_result in {DemoResultType.ANY, DemoResultType.ANY_CHARGE}:
        demo_result = DemoResultType.ALL_DATA

    check_response = _try_load_demo_result(RunCheckResponse, commercial_relationship, f'{country}_{demo_result}') or \
        _try_load_demo_result(RunCheckResponse, commercial_relationship, f'OTHER_{demo_result}') or \
        _try_load_demo_result(RunCheckResponse, commercial_relationship, 'UNSUPPORTED_DEMO_RESULT')
    
    return check_response

def _run_demo_search(
    search_input: SearchInput,
    demo_result: str,
    commercial_relationship: CommercialRelationshipType
) -> SearchResponse:
    country = search_input.country_of_incorporation

    # Default to no matches if we could return any result
    if demo_result in {DemoResultType.ANY}:
        demo_result = DemoResultType.MANY_HITS

    return _try_load_demo_result(SearchResponse, commercial_relationship, f'{country}_{demo_result}') or \
        _try_load_demo_result(SearchResponse, commercial_relationship, f'OTHER_{demo_result}') or \
        _try_load_demo_result(SearchResponse, commercial_relationship, 'UNSUPPORTED_DEMO_RESULT')


def _extract_check_input(req: RunCheckRequest) -> Tuple[List[Error], Optional[CheckInput]]:
    errors = []

    # Extract country of incorporation
    country_of_incorporation = req.check_input.get_country_of_incorporation()
    if country_of_incorporation is None:
        errors.append(Error.missing_required_field(Field.COUNTRY_OF_INCORPORATION))

    if errors:
        return errors, None
    else:
        return [], CheckInput(
            country_of_incorporation=country_of_incorporation
        )

def _extract_search_input(req: RunCheckRequest) -> Tuple[List[Error], Optional[SearchInput]]:
    errors = []

    # Extract country of incorporation
    country_of_incorporation = req.search_input.country_of_incorporation
    if country_of_incorporation is None:
        errors.append(Error.missing_required_field(Field.COUNTRY_OF_INCORPORATION))

    if errors:
        return errors, None
    else:
        return [], CheckInput(
            country_of_incorporation=country_of_incorporation
        )

    

@app.route('/checks', methods=['POST'])
@auth.login_required
@validate_models
def run_check(req: RunCheckRequest) -> RunCheckResponse:
    errors, check_input = _extract_check_input(req)
    if errors:
        return RunCheckResponse.error(errors)

    country = check_input.country_of_incorporation
    if country not in SUPPORTED_COUNTRIES:
        return RunCheckResponse.error([Error.unsupported_country()])

    if req.demo_result is not None:
        return _run_demo_check(check_input, req.demo_result, req.commercial_relationship)

    return RunCheckResponse.error([Error({
        'type': ErrorType.PROVIDER_MESSAGE,
        'message': 'Live checks are not supported',
    })])


@app.route('/search', methods=['POST'])
@auth.login_required
@validate_models
def search(req: SearchRequest) -> SearchResponse:
    errors, search_input = _extract_search_input(req)
    if errors:
        return SearchResponse.error(errors)
    
    country = search_input.country_of_incorporation
    if country not in SUPPORTED_COUNTRIES:
        return SearchResponse.error([Error.unsupported_country()])
    
    if req.demo_result is not None:
        return _run_demo_search(search_input, req.demo_result, req.commercial_relationship)
    
    return SearchResponse.error([Error({
        'type': ErrorType.PROVIDER_MESSAGE,
        'message': 'Live searches are not supported',
    })])
