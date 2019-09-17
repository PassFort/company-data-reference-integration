from datetime import datetime
from zeep import Transport, Client, helpers
from lxml import etree

from app.utils import handle_error
from app.formatters import format_charity


wsdl_url = 'https://apps.charitycommission.gov.uk/Showcharity/API/SearchCharitiesV1/SearchCharitiesV1.asmx?wsdl'


class UKCharitiesCommission:

    def __init__(self, credentials):
        transport = Transport(operation_timeout=5)
        self.client = Client(wsdl_url, transport=transport)
        self.credentials = credentials

    def to_string(self, charity_obj):
        charity_xml = etree.Element('Charity')
        factory = self.client.type_factory('ns0')
        factory.Charity.render(charity_xml, charity_obj)
        return etree.tostring(charity_xml, pretty_print=True)


    def find_charities(self, name):
        return self.client.service.GetCharitiesByName(self.credentials['api_key'], name) or []


    def get_charity_by_number(self, charity_number):
        return self.client.service.GetCharityByRegisteredCharityNumber(self.credentials['api_key'], charity_number)


    def get_charity(self, name):
        results = self.find_charities(name)

        fetched_results = [
            self.get_charity_by_number(charity.RegisteredCharityNumber)
            for charity in results[:10]
        ]

        formatted_results = [
            (self.to_string(raw_charity_obj), format_charity(raw_charity_obj))
            for raw_charity_obj in fetched_results
        ]

        # TODO: Be smarter here
        return formatted_results[0]
