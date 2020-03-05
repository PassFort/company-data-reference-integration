import logging

from flask import Flask, jsonify

from app.api.types import (
    ScreeningRequest,
    validate_model,
)
from app.watchlist_client import (
    APIClient
)

app = Flask(__name__)
logging.getLogger().setLevel(logging.INFO)


@app.route('/health')
def health():
    return jsonify('success')


@app.route('/screening_request', methods=['POST'])
@validate_model(ScreeningRequest)
def run_check(request_data: ScreeningRequest):
    client = APIClient(request_data.credentials)

    search_results = client.run_search(request_data.input_data)

    return jsonify([match.peid for match in search_results.body.matches])


@app.errorhandler(400)
def api_400(error):
    logging.error(error.description)
    return jsonify(errors=[error.description]), 400
