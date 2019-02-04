from xmltodict import unparse, parse
from xml.parsers.expat import ExpatError
from zeep import Transport, Client
from requests.exceptions import ConnectTimeout, HTTPError
from app.api.types import EKYCRequest, Error
from .api.internal_types import EquifaxResponseWithRoot


class EquifaxConnectionError(Exception):
    pass


class EquifaxProviderError(Exception):
    pass


def equifax_client(credentials):
    transport = Transport(timeout=10, operation_timeout=10)
    return Client(f'{credentials.root_url}/efxws/STSRequest.asmx?WSDL',
                  transport=transport,
                  service_name='STSRequest',
                  port_name='STSRequestSoap12')


def generate_input_segment(request_data):
    return unparse({
        'CNCustTransmitToEfx': {
            'CNCustomerInfo': {
                'CustomerCode': request_data.credentials.customer_code,
                'CustomerInfo': {
                    'CustomerNumber': request_data.credentials.customer_number,
                    'SecurityCode': request_data.credentials.security_code
                }
            },
            'CNRequests': {}
        }
    })


def process_equifax_response(raw_response):
    try:
        response = dict(parse(raw_response))
        return {
            'errors': EquifaxResponseWithRoot.from_json(response).get_errors()
        }
    except ExpatError:
        # This means we didn't get an xml back
        return {
            'errors': [Error.provider_unknown_error(raw_response)]
        }
    return {
        'errors': []
    }


def ekyc_request(request_data: EKYCRequest):
    try:
        client = equifax_client(request_data.credentials)
    except ConnectTimeout as e:
        raise EquifaxConnectionError(e)
    except HTTPError as e:
        raise EquifaxProviderError(e)

    xml_input = generate_input_segment(request_data)
    raw_response = client.service.Submit(InputSegment=xml_input)

    return process_equifax_response(raw_response)
