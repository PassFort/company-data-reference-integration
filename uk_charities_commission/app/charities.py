from datetime import datetime
from zeep import Transport, Client, helpers
import json

from app.utils import handle_error
from app.formatters import format_charity


wsdl_url = 'https://apps.charitycommission.gov.uk/Showcharity/API/SearchCharitiesV1/SearchCharitiesV1.asmx?wsdl'


def to_dict(input_obj):
    input_dict = helpers.serialize_object(input_obj)
    return json.loads(json.dumps(input_dict, default=str))


def get_client():
    transport = Transport(operation_timeout=5)
    return Client(wsdl_url, transport=transport)


def find_charities(client, name, credentials):
    return client.service.GetCharitiesByName(credentials['api_key'], name) or []


def get_charity_by_number(client, charity_number, credentials):
    return client.service.GetCharityByRegisteredCharityNumber(credentials['api_key'], charity_number)


def get_charity(name, credentials):
    client = get_client()

    results = find_charities(client, name, credentials)

    fetched_results = [
        get_charity_by_number(client, charity['RegisteredCharityNumber'], credentials)
        for charity in results[:10]
    ]

    formatted_results = [(to_dict(data), format_charity(data)) for data in fetched_results]

    return formatted_results[0]
