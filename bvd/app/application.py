import os
from flask import Flask, jsonify, request
from raven.contrib.flask import Sentry

from bvd.format_utils import CustomJSONEncoder
from bvd.utils import match, get_data, get_query_string, BvDServiceException, \
    REQUEST_EXCEPTIONS, BvDEmptyResponseException, BvDError, \
    get_demo_data, get_demo_search_data, match, country_alpha2to3
from bvd.registry import format_registry_data
from bvd.ownership import format_ownership_data

app = Flask(__name__)
app.json_encoder = CustomJSONEncoder

sentry_url = os.environ.get('SENTRY_URL')
if sentry_url:
    sentry = Sentry(
        app,
        logging=True,
        level=logging.ERROR, dsn=sentry_url
    )


def get_bvd_id(credentials, input_data):
    bvd_id = input_data.get('bvd_id')
    if bvd_id is None:
        error, result = run_check(lambda: match(credentials, {
            'Country': input_data['country_of_incorporation'],
            'NationalId': input_data['number'],
        }))
        if error:
            return error, result
        elif result:
            return None, result['BvDID']

    return None, bvd_id


def run_check(executor):
    try:
        results = executor()
        raw_data = results[0]
        return None, raw_data
    except REQUEST_EXCEPTIONS as e:
        return BvDError(e), None
    except BvDServiceException as e:
        return BvDError(e), None
    except BvDEmptyResponseException:
        return None, None


@app.route('/health')
def health():
    return jsonify('success')


@app.route('/registry-check', methods=['POST'])
def registry_check():
    req_body = request.json
    input_data = req_body['input_data']
    credentials = req_body['credentials']
    is_demo = req_body['is_demo']

    if is_demo:
        return jsonify(get_demo_data(
            check='registry',
            country_code=input_data.get('country_of_incorporation'),
            bvd_id=input_data.get('bvd_id'),
            company_number=input_data.get('number'),
        ))

    output_data = None
    raw_data = None

    error, bvd_id = get_bvd_id(credentials, input_data)
    if bvd_id:
        query = get_query_string('registry')
        error, raw_data = run_check(
            lambda: get_data(credentials, [bvd_id], query)
        )

        if raw_data:
            try:
                output_data = format_registry_data(raw_data)
            except Exception as e:
                error = BvDError(e)

    return jsonify(
        output_data=output_data if output_data else {},
        raw=raw_data,
        errors=[error] if error else [],
        price=0,
    )


@app.route('/ownership-check', methods=['POST'])
def ownership_check():
    req_body = request.json
    input_data = req_body['input_data']
    credentials = req_body['credentials']
    is_demo = req_body['is_demo']

    if is_demo:
        return jsonify(get_demo_data(
            check='ownership',
            country_code=input_data.get('country_of_incorporation'),
            bvd_id=input_data.get('bvd_id'),
            company_number=input_data.get('number'),
        ))

    output_data = None
    raw_data = None

    error, bvd_id = get_bvd_id(credentials, input_data)
    if bvd_id:
        query = get_query_string('ownership')
        error, raw_data = run_check(
            lambda: get_data(credentials, [bvd_id], query)
        )
        if raw_data:
            try:
                output_data = format_ownership_data(raw_data)
            except Exception as e:
                error = BvDError(e)

    return jsonify(
        output_data=output_data if output_data else {},
        raw=raw_data,
        errors=[error] if error else [],
        price=0,
    )


@app.route('/search', methods=['POST'])
def company_search():
    req_body = request.json
    input_data = req_body['input_data']
    credentials = req_body['credentials']
    is_demo = req_body.get('is_demo')

    raw_data = []
    error = None
    if is_demo:
        raw_data = get_demo_search_data(input_data['country'])
    else:
        try:
            raw_data = match(credentials, input_data)
        except Exception as e:
            error = BvDError(e)

    candidates = [{
        'name': company['Name'],
        'number': company['NationalId'],
        'country': country_alpha2to3(company['Country']),
        'bvd_id': company['BvDID'],
        'bvd9': company['BvD9'],
        'status': company.get('Status', 'Unknown'),
    } for company in raw_data if company.get('NationalId')]

    returnval = jsonify(
        output_data=candidates,
        raw=raw_data,
        errors=[error] if error else [],
    )

    return returnval
