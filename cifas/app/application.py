import os
import logging
from flask import Flask, jsonify, abort
from raven.contrib.flask import Sentry
from passfort.cifas_check import CifasCheck
from cifas import CifasAPIClient, CifasConnectionError, CifasHTTPError
from cifas.search import FullSearchRequest
from passfort_demo import get_demo_response


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


@app.route('/cifas-search', methods=['POST'])
def run_cifas_search():
    cifas_search = CifasCheck.from_dict(request.json)
    error = None
    if cifas_search.is_demo:
        output_data = get_demo_response(cifas_search)
    else:
        try:
            api_client = CifasApiClient(cifas_search.config, cifas_search.credentials)
            request = FullSearchRequest.from_passfort_entity_data(cifas_search.input_data)
            response = api_client.full_search(request)
            output_data = response.to_passfort_output_data()
        except CifasConnectionError:
            abort(500)
        except CifasHTTPError:
            abort(500)

    return jsonify(
        output_data=output_data,
        errors=[error] if error else [],
        price=0,
    )
