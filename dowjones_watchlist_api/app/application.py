import logging

from flask import Flask, jsonify

from app.api.types import (
    Error,
    ScreeningRequest,
    ScreeningResponse,
    MatchEvent,
    MatchEventType,
    validate_model,
)
from app.watchlist_client import (
    APIClient,
    DemoClient,
)

app = Flask(__name__)
logging.getLogger().setLevel(logging.INFO)


PROVIDER_NAME = 'Dow Jones Watchlist API'


@app.route('/health')
def health():
    return jsonify('success')


@app.route('/screening_request', methods=['POST'])
@validate_model(ScreeningRequest)
def run_check(request_data: ScreeningRequest):
    if request_data.is_demo:
        client = DemoClient(request_data.credentials)
    else:
        client = APIClient(request_data.credentials)

    search_results = client.run_search(request_data.input_data)

    data_results = [
        {
            'icon': match.payload.risk_icons.icons[0],
            'name': match.payload.matched_name,
            'score': match.score,
            'record': client.fetch_data_record(match.peid)
        }
        for match in search_results.body.matches
    ]

    return jsonify(ScreeningResponse({
        'errors': [],
        'events': [MatchEvent({
            'event_type': MatchEventType.from_risk_icon(results['icon']).value,
            'match_id': results['record'].person.peid,
            'provider_name': PROVIDER_NAME,
            'match_name': results['name'],
            'score': results['score'],
        }) for results in data_results],
    }).to_primitive())


@app.errorhandler(400)
def api_400(error):
    logging.error(error)
    return jsonify(ScreeningResponse({
        'errors': [Error.bad_api_request(error.description)]
    }).to_primitive()), 400


@app.errorhandler(500)
def api_500(error):
    import traceback
    logging.error(traceback.format_exc())
    return jsonify(errors=[Error.from_exception(error)]), 500
