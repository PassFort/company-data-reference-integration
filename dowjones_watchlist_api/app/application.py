import logging

from flask import Flask, jsonify

from app.api.types import (
    Associate,
    CountryMatchData,
    CountryMatchType,
    DateMatchData,
    DateMatchType,
    Error,
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


@app.route('/health')
def health():
    return jsonify('success')


@app.route('/screening_request', methods=['POST'])
@validate_model(ScreeningRequest)
def run_check(request_data: ScreeningRequest):
    if request_data.is_demo:
        client = DemoClient(request_data.config, request_data.credentials)
    else:
        client = APIClient(request_data.config, request_data.credentials)

    search_results = client.run_search(request_data.input_data)

    def fetch_associate_data(associate_match_data):
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

    def event_from_match(match):
        record = client.fetch_data_record(match.peid)
        risk_icon = match.payload.risk_icons.icons[0]
        event_type = MatchEventType.from_risk_icon(risk_icon)

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
        }) if event_type == MatchEventType.PEP_FLAG else None

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
        ] if event_type == MatchEventType.SANCTION_FLAG else None

        associates = [
            associate for associate in
            (fetch_associate_data(associate) for associate in record.person.associates)
            if associate is not None
        ]

        return MatchEvent({
            'event_type': event_type.value,
            'match_id': record.person.peid,
            'provider_name': PROVIDER_NAME,
            'match_custom_label': risk_icon,
            'match_name': match.payload.matched_name,
            'match_dates': [match.date for match in date_matches] if date_matches else None,
            'match_dates_data': date_matches,
            'score': match.score,
            'aliases': [
                value.name.join() for value in record.person.name_details.values
                if value.name.type_.lower() == 'also known as'
            ],
            'pep': pep_data,
            'sanctions': sanctions_data,
            'profile_notes': record.person.watchlist_content.profile_notes,
            'sources': [Source({'name': source.reference}) for source in record.person.watchlist_content.sources],
            'associates': associates,
            'match_countries': [match.country_code for match in country_matches],
            'match_countries_data': country_matches,
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
