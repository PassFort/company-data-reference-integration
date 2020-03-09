import logging

from flask import Flask, jsonify

from app.api.types import (
    CountryMatchType,
    Error,
    Gender,
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

    def event_from_match(match):
        record = client.fetch_data_record(match.peid)
        risk_icon = match.payload.risk_icons.icons[0]
        event_type = MatchEventType.from_risk_icon(risk_icon)

        gender = Gender.from_dowjones(record.person.gender)

        country_match_types = [
            CountryMatchType.from_dowjones(value.country_type)
            for value in record.person.country_details.country_values
        ]

        country_matches = [
            value.country.iso3_country_code
            for value in record.person.country_details.country_values
        ]

        return MatchEvent({
            'event_type': event_type.value,
            'match_id': record.person.peid,
            'provider_name': PROVIDER_NAME,
            'match_custom_label': risk_icon,
            'match_name': match.payload.matched_name,
            'score': match.score,
            'match_countries': country_matches,
            'country_match_types': [ty.value for ty in country_match_types],

            'gender': gender.value if gender else None,
            'deceased': record.person.deceased,
        })

    events = [
        event_from_match(match) for match in search_results.body.matches
    ]

    return jsonify(ScreeningResponse({
        'errors': [],
        'events': events,
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
