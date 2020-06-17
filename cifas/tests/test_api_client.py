import responses
from unittest import TestCase
from requests.exceptions import HTTPError, ConnectionError, SSLError
from zeep.exceptions import Fault

from cifas import CifasAPIClient, CifasConnectionError, CifasHTTPError, CifasFaultError
from cifas.search import FullSearchRequest, IndividualParty, StructuredAddress
from passfort.cifas_check import CifasConfig, CifasCredentials
from datetime import date
from tests import MATCH_RESPONSE


class TestAPIClient(TestCase):
    def create_client(self):
        return CifasAPIClient(CifasConfig(
            product_code='PXXX',
            user_name='TestCustomer1',
            search_type='XXX',
            use_uat=True,
            member_id=1105
        ), CifasCredentials(
            cert='XXXXXXXXX'
        ))

    @responses.activate
    def test_search_success(self):
        responses.add(
            responses.POST,
            'https://training-services.find-cifas.org.uk/Direct/CIFAS/Request.asmx',
            body=MATCH_RESPONSE,
            content_type='text/xml; charset=utf-8',
        )

        client = self.create_client()
        response = client.full_search(FullSearchRequest(
            Product='PXXX',
            SearchType='XX',
            MemberSearchReference='a4w6wq4465',
            Party=IndividualParty(
                FirstName='Malvi',
                Surname='Ritsa',
                BirthDate=date(year=1950, month=5, day=18),
                EmailAddress='malviritsa@mymail.com',
                Address=StructuredAddress(
                    HouseNumber='6',
                    Postcode='PE20 3LW',
                ),
            ),
        ))

        self.assertEqual(type(response.MemberSearchReference), str)
        self.assertEqual(type(response.FINDsearchReference), int)

    @responses.activate
    def test_search_connection_error(self):
        responses.add(
            responses.POST,
            'https://training-services.find-cifas.org.uk/Direct/CIFAS/Request.asmx',
            body=ConnectionError(),
        )

        client = self.create_client()
        with self.assertRaises(CifasConnectionError):
            client.full_search(FullSearchRequest(
                Product='PXXX',
                SearchType='XX',
                MemberSearchReference='a4w6wq4465',
                Party=IndividualParty(
                    FirstName='Malvi',
                    Surname='Ritsa',
                    BirthDate=date(year=1950, month=5, day=18),
                    EmailAddress='malviritsa@mymail.com',
                    Address=StructuredAddress(
                        HouseNumber='6',
                        Postcode='PE20 3LW',
                    ),
                ),
            ))

    @responses.activate
    def test_search_ssl_error(self):
        responses.add(
            responses.POST,
            'https://training-services.find-cifas.org.uk/Direct/CIFAS/Request.asmx',
            body=SSLError(),
        )

        client = self.create_client()
        with self.assertRaises(CifasConnectionError):
            client.full_search(FullSearchRequest(
                Product='PXXX',
                SearchType='XX',
                MemberSearchReference='a4w6wq4465',
                Party=IndividualParty(
                    FirstName='Malvi',
                    Surname='Ritsa',
                    BirthDate=date(year=1950, month=5, day=18),
                    EmailAddress='malviritsa@mymail.com',
                    Address=StructuredAddress(
                        HouseNumber='6',
                        Postcode='PE20 3LW',
                    ),
                ),
            ))

    @responses.activate
    def test_search_http_error(self):
        responses.add(
            responses.POST,
            'https://training-services.find-cifas.org.uk/Direct/CIFAS/Request.asmx',
            body=HTTPError(),
        )

        client = self.create_client()
        with self.assertRaises(CifasHTTPError):
            client.full_search(FullSearchRequest(
                Product='PXXX',
                SearchType='XX',
                MemberSearchReference='a4w6wq4465',
                Party=IndividualParty(
                    FirstName='Malvi',
                    Surname='Ritsa',
                    BirthDate=date(year=1950, month=5, day=18),
                    EmailAddress='malviritsa@mymail.com',
                    Address=StructuredAddress(
                        HouseNumber='6',
                        Postcode='PE20 3LW',
                    ),
                ),
            ))

    @responses.activate
    def test_validation_error(self):
        responses.add(
            responses.POST,
            'https://training-services.find-cifas.org.uk/Direct/CIFAS/Request.asmx',
            body='<soap:Envelope xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/">'
                 '<soap:Body>'
                 '<soap:Fault>'
                 '<detail xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:xsd="http://www.w3.org/2001/XMLSchema">'
                 '<SchemaError xmlns="http://fault.find-cifas.org.uk">'
                 '<Element>http://objects.find-cifas.org.uk/Direct:Postcode</Element>'
                 '<Value>917801306</Value>'
                 '<Error>The Pattern constraint failed.</Error>'
                 '<Type>String</Type>'
                 '<Schema>http://objects.find-cifas.org.uk/Direct</Schema>'
                 '<LineNumber>2</LineNumber>'
                 '<CharacterPosition>1036</CharacterPosition>'
                 '</SchemaError></detail>'
                 '</soap:Fault>'
                 '</soap:Body>'
                 '</soap:Envelope>'
        )

        client = self.create_client()
        with self.assertRaises(CifasFaultError):
            client.full_search(FullSearchRequest(
                Product='PXXX',
                SearchType='XX',
                MemberSearchReference='a4w6wq4465',
                Party=IndividualParty(
                    FirstName='Malvi',
                    Surname='Ritsa',
                    BirthDate=date(year=1950, month=5, day=18),
                    EmailAddress='malviritsa@mymail.com',
                    Address=StructuredAddress(
                        HouseNumber='6',
                        Postcode='PE20 3LW',
                    ),
                ),
            ))