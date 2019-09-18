import os
import logging
from flask import Flask, jsonify, request
from raven.contrib.flask import Sentry
from schemad_types.serialization import coerce_untracked

from passfort_data_structure.entities.company_data import CompanyData
from passfort_data_structure.misc.errors import EngineError, ProviderError

from app.UKCharitiesCommission import UKCharitiesCommission

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


@app.route('/charity-check', methods=['POST'])
def charity_check():
    input_data = request.json['input_data']
    credentials = request.json['credentials']

    errors = []

    metadata = input_data.get('metadata', {})

    try:
        name = metadata['name']
    except KeyError:
        errors.append({'message': 'Missing company name in input'})

    country_of_incorporation = metadata.get('country', 'GBR')
    if country_of_incorporation != 'GBR':
        errors.append(coerce_untracked(
            EngineError.country_not_supported(country_of_incorporation)
        ))

    if not credentials.get('api_key'):
        errors.append({'message': 'Missing apikey'})

    if len(errors):
        return jsonify(errors=errors)

    charities_commission = UKCharitiesCommission(credentials)
    raw, response = charities_commission.get_charity(name, metadata.get('number'))

    return jsonify(
        output_data=coerce_untracked(response) if response else None,
        raw=raw.decode('utf8') if raw else None,
        errors=[],
        price=0,
    )
