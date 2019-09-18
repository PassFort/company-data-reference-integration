from datetime import datetime
from zeep import Transport, Client, helpers
from lxml import etree

from app.utils import handle_error, is_active, permissive_string_compare
from app.formatters import format_charity


wsdl_url = 'https://apps.charitycommission.gov.uk/Showcharity/API/SearchCharitiesV1/SearchCharitiesV1.asmx?wsdl'


def is_match(charity, company_number, company_name):
    return permissive_string_compare(charity.CharityName, company_name) or \
        permissive_string_compare(charity.RegisteredCompanyNumber, company_number)


class UKCharitiesCommission:

    def __init__(self, credentials):
        transport = Transport(operation_timeout=5)
        self.client = Client(wsdl_url, transport=transport)
        self.credentials = credentials

    def __value_to_xml(self, charity_obj):
        charity_xml = etree.Element('Charity')
        factory = self.client.type_factory('ns0')
        factory.Charity.render(charity_xml, charity_obj)
        return etree.tostring(charity_xml, pretty_print=True)


    def find_charities(self, name):
        return self.client.service.GetCharitiesByName(self.credentials['api_key'], name) or []


    def get_charity_by_number(self, charity_number):
        return self.client.service.GetCharityByRegisteredCharityNumber(self.credentials['api_key'], charity_number)


    def __pick_best_charity(self, candidates, company_number, company_name):
        candidates = [c for c in candidates if is_match(c, company_number, company_name)]

        if len(candidates) is 0:
            return None

        if len(candidates) is 1:
            return candidates[0]

        candidatees = [c for c in candidates if is_active(c)]


        if len(candidates) is 0:
            return None

        return candidates[0]


    def get_charity(self, name, number):
        results = self.find_charities(name)

        fetched_results = [
            self.get_charity_by_number(charity.RegisteredCharityNumber)
            for charity in results[:10]
        ]

        picked_result = self.__pick_best_charity(fetched_results, number, name)

        if picked_result:
            return (
                self.__value_to_xml(picked_result),
                format_charity(picked_result)
            )

        return (None, None)
