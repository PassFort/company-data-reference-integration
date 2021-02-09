import json
import os
import re

from dataclasses import dataclass
from typing import Optional, List, Tuple

from flask import Flask, send_file, request, abort, Response

from app.api import (
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
    name: Optional[str]
    number: Optional[str]
    country_of_incorporation: Optional[str]


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

    filename = f'../static/demo_results/{_sanitize_filename(name)}.json'

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
    if demo_result in {
        DemoResultType.ANY,
        DemoResultType.ANY_CHARGE,
        DemoResultType.COMPANY_INACTIVE,
        DemoResultType.COMPANY_NAME_MISMATCH,
        DemoResultType.COMPANY_NUMBER_MISMATCH,
        DemoResultType.COMPANY_COUNTRY_OF_INCORPORATION_MISMATCH,
    }:
        check_response = (
            _try_load_demo_result(RunCheckResponse, commercial_relationship, DemoResultType.ALL_DATA)
        )
    else:
        check_response = (
            _try_load_demo_result(RunCheckResponse, commercial_relationship, f'{demo_result}')
            or _try_load_demo_result(RunCheckResponse, commercial_relationship, 'UNSUPPORTED_DEMO_RESULT')
        )

    check_response.patch_to_match_input(check_input)

    if demo_result == DemoResultType.COMPANY_INACTIVE:
        check_response.check_output.metadata.is_active = False
        check_response.check_output.metadata.is_active_details = 'Inactive'
    elif demo_result == DemoResultType.COMPANY_NAME_MISMATCH:
        check_response.check_output.metadata.name = f'NOT {check_input.name}' if check_input.name else 'Example Co.'
    elif demo_result == DemoResultType.COMPANY_NUMBER_MISMATCH:
        check_response.check_output.metadata.number = f'NOT {check_input.number}' if check_input.number else '123456'
    elif demo_result == DemoResultType.COMPANY_COUNTRY_OF_INCORPORATION_MISMATCH:
        check_response.check_output.metadata.country_of_incorporation = 'GBR' if check_input.country_of_incorporation != 'GBR' else 'FRA'

    return check_response


def _run_demo_search(
    search_input: SearchInput,
    demo_result: str,
    commercial_relationship: CommercialRelationshipType
) -> SearchResponse:
    # Default to full match if we can return any result
    if demo_result in {DemoResultType.ANY}:
        demo_result = DemoResultType.MANY_HITS

    return _try_load_demo_result(SearchResponse, commercial_relationship, f'{demo_result}') or \
        _try_load_demo_result(SearchResponse, commercial_relationship, 'UNSUPPORTED_DEMO_RESULT')


def _extract_check_input(req: RunCheckRequest) -> Tuple[List[Error], Optional[CheckInput]]:
    errors = []

    # Extract country of incorporation
    country_of_incorporation = req.check_input.get_country_of_incorporation()
    if country_of_incorporation is None:
        errors.append(Error.missing_required_field(Field.COUNTRY_OF_INCORPORATION))

    name = req.check_input.get_company_name()
    number = req.check_input.get_company_number()

    if errors:
        return errors, None
    else:
        return [], CheckInput(
            name=name,
            number=number,
            country_of_incorporation=country_of_incorporation,
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
        return [], SearchInput(
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
