from datetime import datetime
from zeep import Transport, Client, helpers
from lxml import etree

from app.utils import handle_error
from app.formatters import format_charity


wsdl_url = 'https://apps.charitycommission.gov.uk/Showcharity/API/SearchCharitiesV1/SearchCharitiesV1.asmx?wsdl'


def to_string(client, charity_obj):
    charity_xml = etree.Element('Charity')
    factory = client.type_factory('ns0')
    factory.Charity.render(charity_xml, charity_obj)
    return etree.tostring(charity_xml)


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

    formatted_results = [(to_string(client, data), format_charity(data)) for data in fetched_results]

    return formatted_results[0]
