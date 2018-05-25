import os
import logging
from flask import Flask, jsonify, request
from raven.contrib.flask import Sentry
from requests.exceptions import RequestException, HTTPError
from json import JSONDecodeError
from schemad_types.serialization import coerce_untracked

from passfort_data_structure.entities.company_data import CompanyData
from passfort_data_structure.misc.errors import EngineError, ProviderError

from app.companies import request_company_search
from app.officers import request_officers
from app.metadata import get_metadata, CompanyTypeError
from app.shareholders import request_shareholders
from app.utils import DueDilServiceException
from app.charities import get_charity

app = Flask(__name__)

sentry_url = os.environ.get('SENTRY_URL')
if sentry_url:
    sentry = Sentry(
        app,
        logging=True,
        level=logging.ERROR, dsn=sentry_url
    )


global_supported_countries = {
    'ALB': 'al',
    'BEL': 'be',
    'BHS': 'bs',
    'BMU': 'bm',
    'CHE': 'ch',
    'CYP': 'cy',
    'DEU': 'de',
    'DNK': 'dk',
    'FIN': 'fi',
    'FRA': 'fr',
    'GBR': 'gb',
    'GGY': 'gg',
    'GRL': 'gl',
    'HKG': 'hk',
    'IMN': 'im',
    'IRL': 'ie',
    'ISL': 'is',
    'ISR': 'il',
    'JEY': 'je',
    'LIE': 'li',
    'LUX': 'lu',
    'LVA': 'lv',
    'MLT': 'mt',
    'MNE': 'me',
    'NLD': 'nl',
    'NOR': 'no',
    'POL': 'pl',
    'ROU': 'ro',
    'SVK': 'sk',
    'SVN': 'sl',
    'SWE': 'se',
}

basic_supported_countries = {
    'GBR': 'gb',
    'IRL': 'ie',
}

base_request_exceptions = (RequestException, JSONDecodeError, HTTPError, KeyError)


@app.route('/health')
def health():
    return jsonify('success')


@app.route('/registry-check', methods=['POST'])
def registry_check():
    input_data = request.json['input_data']
    config = request.json['config']
    credentials = request.json['credentials']

    company_number = input_data['metadata']['number']['v']
    country_of_incorporation = input_data['metadata']['country_of_incorporation']['v']

    has_global_coverage = config.get('has_global_coverage', False)
    supported_countries = global_supported_countries if has_global_coverage else basic_supported_countries

    if country_of_incorporation not in supported_countries:
        return jsonify(errors=coerce_untracked([
            EngineError.country_not_supported(country_of_incorporation)
        ]))

    country_code = supported_countries[country_of_incorporation]

    errors = []
    metadata, raw_metadata, officers, raw_officers = None, None, None, None

    try:
        raw_metadata, metadata = get_metadata(country_code, company_number, credentials)
    except CompanyTypeError as e:
        errors.append(
            ProviderError.provider_unknown_error('DueDil', e.args[0])
        )
    except base_request_exceptions as e:
        errors.append(
            ProviderError.provider_connection_error('DueDil', 'Company metdata request failed')
        )

    try:
        if metadata is not None:
            raw_officers, officers = request_officers(country_code, company_number, credentials)
    except base_request_exceptions as e:
        errors.append(
            ProviderError.provider_connection_error('DueDil', 'Officers request failed')
        )

    raw_response = {
        'metadata': raw_metadata,
        'directors': raw_officers,
    } if raw_metadata else None

    response = CompanyData(
        metadata=metadata,
        officers={'directors': officers} if officers else None,
    ) if metadata else None

    return jsonify(
        output_data=coerce_untracked(response),
        raw=raw_response,
        errors=coerce_untracked(errors),
        price=0,
    )


@app.route('/ownership-check', methods=['POST'])
def ownership_check():
    input_data = request.json['input_data']
    config = request.json['config']
    credentials = request.json['credentials']

    company_number = input_data['metadata']['number']['v']
    country_of_incorporation = input_data['metadata']['country_of_incorporation']['v']

    has_global_coverage = config.get('has_global_coverage', False)
    supported_countries = global_supported_countries if has_global_coverage else basic_supported_countries

    if country_of_incorporation not in supported_countries:
        return jsonify(errors=coerce_untracked([
            EngineError.country_not_supported(country_of_incorporation)
        ]))

    country_code = supported_countries[country_of_incorporation]

    try:
        _, metadata = get_metadata(country_code, company_number, credentials)
        if not metadata:
            return jsonify(output_data=None, raw=None, errors=None, price=0)
    except base_request_exceptions as e:
        return jsonify(errors=coerce_untracked([
            ProviderError.provider_connection_error('DueDil', '- Company metdata request failed')
        ]))

    raw_shareholders, shareholders = None, None

    try:
        raw_shareholders, shareholders = request_shareholders(country_code, company_number, credentials)
    except base_request_exceptions:
        return jsonify(errors=coerce_untracked([
            ProviderError.provider_connection_error('DueDil', '- Shareholders request failed')
        ]))

    raw_response = {
        'shareholders': raw_shareholders,
    }

    response = CompanyData(
        ownership_structure={
            'shareholders': shareholders,
        } if shareholders else None
    )

    return jsonify(
        output_data=coerce_untracked(response),
        raw=raw_response,
        errors=[],
        price=0,
    )


@app.route('/company-search', methods=['POST'])
def company_search():
    input_data = request.json['input_data']
    config = request.json['config']
    credentials = request.json['credentials']

    country_of_incorporation = input_data['country']

    has_global_coverage = config.get('has_global_coverage', False)
    supported_countries = global_supported_countries if has_global_coverage else basic_supported_countries

    if country_of_incorporation not in supported_countries:
        return jsonify(errors=coerce_untracked([
            EngineError.country_not_supported(country_of_incorporation)
        ]))

    country_code = supported_countries[country_of_incorporation]
    search_term = input_data['query']

    try:
        raw_companies, companies = request_company_search(country_code, search_term, credentials)
    except base_request_exceptions as e:
        return jsonify(errors=coerce_untracked([
            ProviderError.provider_connection_error('DueDil', f'- Company search request failed. {e}')
        ]))

    return jsonify(
        output_data=companies,
        raw=raw_companies,
        errors=[],
        price=0
    )


@app.route('/charity-check', methods=['POST'])
def charity_check():
    input_data = request.json['input_data']
    credentials = request.json['credentials']

    company_number = input_data['metadata']['number']
    country_of_incorporation = input_data['metadata']['country_of_incorporation']

    supported_countries = {
        'GBR': 'gb'
    }

    if country_of_incorporation not in supported_countries:
        return jsonify(errors=coerce_untracked([
            EngineError.country_not_supported(country_of_incorporation)
        ]))

    country_code = supported_countries[country_of_incorporation]

    raw_response, response = get_charity(country_code, company_number, credentials)

    return jsonify(
        output_data=coerce_untracked(response),
        raw=raw_response,
        errors=[],
        price=0,
    )
