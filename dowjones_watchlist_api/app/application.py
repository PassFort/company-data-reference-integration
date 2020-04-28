import logging
import traceback
from collections import defaultdict

from flask import Flask, jsonify
import requests

from app.api.types import (
    Associate,
    CountryMatchData,
    CountryMatchType,
    DateMatchData,
    DateMatchType,
    Error,
    Location,
    Gender,
    MatchEvent,
    MatchEventType,
    OccupationCategory,
    PepData,
    PepRole,
    SanctionsData,
    ScreeningRequest,
    ScreeningResponse,
    Source,
    TimePeriod,
    validate_model,
)
from app.watchlist_client import (
    APIClient,
    DemoClient,
)

app = Flask(__name__)
logging.getLogger().setLevel(logging.INFO)


PROVIDER_NAME = 'Dow Jones Watchlist API'


def brand_text():
    from datetime import datetime
    year = datetime.now().year
    return f'Powered By Dow Jones. Copyright © {year} Dow Jones & Company, Inc. All rights reserved.'


@app.route('/health')
def health():
    return jsonify('success')


def fetch_associate_data(client, associate_match_data):
    record = client.fetch_data_record(associate_match_data.peid)
    if record.person is None:
        # Associate might not be a person and we don't support
        # other entity types in this integration
        return None

    name = next((
        value.name.join()
        for value in record.person.name_details.values
        if value.name.type_.lower() == 'primary name'
    ), None)

    watchlist_content = record.person.watchlist_content
    been_pep = any(
        description.text.lower() == 'politically exposed person (pep)'
        for description in watchlist_content.descriptions
    )
    been_sanctioned = any(
        description.text.lower() == 'sanctions lists'
        for description in watchlist_content.descriptions
    )

    date_matches = [
        DateMatchData({
            'type': DateMatchType.from_dowjones(date.type_).value if date.type_ else None,
            'date': date.to_partial_date_string(),
        }) for date in record.person.date_details.dates
    ] if record.person.date_details else []

    return Associate({
        'name': name,
        'association': associate_match_data.relationship,
        'is_pep': been_pep and watchlist_content.active_status.is_active,
        'was_pep': been_pep and not watchlist_content.active_status.is_active,
        'is_sanction': been_sanctioned and watchlist_content.active_status.is_active,
        'was_sanction': been_sanctioned and not watchlist_content.active_status.is_active,
        'dobs': [
            match.date
            for match in date_matches
            if match.type_ == DateMatchType.DOB.value
        ],
        'inactive_as_pep_dates': [
            match.date
            for match in date_matches
            if match.type_ == DateMatchType.END_OF_PEP.value
        ],
        'deceased_dates': [
            match.date
            for match in date_matches
            if match.type_ == DateMatchType.DECEASED.value
        ],
    })


def events_from_match(client, match):
    record = client.fetch_data_record(match.peid)

    risk_icon_map = defaultdict(list)
    for icon in match.payload.risk_icons.icons:
        risk_icon_map[MatchEventType.from_risk_icon(icon)].append(icon)

    gender = Gender.from_dowjones(record.person.gender)

    country_matches = [
        CountryMatchData({
            'type': CountryMatchType.from_dowjones(value.country_type).value,
            'country_code': value.country.iso3_country_code,
        }) for value in record.person.country_details.country_values
    ]

    date_matches = [
        DateMatchData({
            'type': DateMatchType.from_dowjones(date.type_).value if date.type_ else None,
            'date': date.to_partial_date_string(),
        }) for date in record.person.date_details.dates
    ] if record.person.date_details else None

    pep_data = PepData({
        'roles': [
            PepRole({
                'name': role.title.text,
                'tier': OccupationCategory(role.title.category).pep_tier,
                'is_current': role.type_ == 'Primary Occupation',
                'from_date': role.title.since_partial_date,
                'to_date': role.title.to_partial_date,
            }) for role in record.person.watchlist_content.roles
        ]
    })

    sanctions_data = [
        SanctionsData({
            'type': 'sanction',
            'issuer': sanction.list_provider_name,
            'list': sanction.list_,
            'is_current': sanction.status.lower() == 'current',
            'time_periods': [TimePeriod({
                'from_date': sanction.since_partial_date,
                'to_date': sanction.to_partial_date,
            })]
        }) for sanction in record.person.watchlist_content.sanctions
    ]

    associates = [
        associate for associate in
        (fetch_associate_data(client, associate) for associate in record.person.associates)
        if associate is not None
    ]

    locations = [
        Location({
            'type': 'BIRTH',
            'region': birth_place.region,
            'country': birth_place.country.iso3_country_code,
            'city': birth_place.place_name,
        })
        for birth_place in record.person.birth_place_details.values
    ] if record.person.birth_place_details else []


    def build_event(event_type, label):
        event = MatchEvent({
            'event_type': event_type.value,
            'match_id': record.person.peid,
            'provider_name': PROVIDER_NAME,
            'brand_text': brand_text(),
            'match_name': next(
                (value.name.join() for value in record.person.name_details.values
                 if value.name.type_.lower() == 'primary name'),
                match.payload.primary_name
            ),
            'match_custom_label': label,
            'match_dates': [match.date for match in date_matches] if date_matches else None,
            'match_dates_data': date_matches,
            'aliases': [
                value.name.join() for value in record.person.name_details.values
                if value.name.type_.lower() == 'also known as'
            ],
            'profile_notes': record.person.watchlist_content.profile_notes,
            'sources': [Source({'name': source.reference}) for source in record.person.watchlist_content.sources],
            'associates': associates,
            'locations': locations,
            'match_countries': [match.country_code for match in country_matches],
            'match_countries_data': country_matches,
            'gender': gender.value if gender else None,
            'deceased': record.person.deceased,
        })

        if event_type is MatchEventType.PEP_FLAG:
            event.pep = pep_data

        if event_type is MatchEventType.SANCTION_FLAG:
            event.sanctions = sanctions_data

        return event

    return [
        build_event(event_type, icon)
        for event_type in risk_icon_map
        for icon in risk_icon_map[event_type]
    ]


@app.route('/screening_request', methods=['POST'])
@validate_model(ScreeningRequest)
def run_check(request_data: ScreeningRequest):
    if request_data.is_demo:
        client = DemoClient(request_data.config, request_data.credentials)
    else:
        client = APIClient(request_data.config, request_data.credentials)

    search_results = client.run_search(request_data.input_data)

    events = [
        event
        for match in search_results.body.matches
        for event in events_from_match(client, match)
    ]

    return jsonify(ScreeningResponse({
        'errors': [],
        'events': events,
    }).to_primitive())


@app.errorhandler(requests.exceptions.HTTPError)
def dowjones_request_failure(error):
    logging.error(error)
    if error.response.status_code in {403, 401}:
        return jsonify(ScreeningResponse({
            'errors': [Error.bad_credentials()]
        }).to_primitive()), 403
    else:
        logging.error(traceback.format_exc())
        return jsonify(errors=[Error.from_exception(error)]), 500


@app.errorhandler(400)
def api_400(error):
    logging.error(error)
    return jsonify(ScreeningResponse({
        'errors': [Error.bad_api_request(error.description)]
    }).to_primitive()), 400


@app.errorhandler(500)
def api_500(error):
    logging.error(traceback.format_exc())
    return jsonify(errors=[Error.from_exception(error)]), 500
