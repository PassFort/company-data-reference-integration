from collections import OrderedDict
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
    root = OrderedDict()
    auth_dict = OrderedDict([
        ('CustomerCode', request_data.credentials.customer_code),
        ('CustomerInfo', OrderedDict([
            ('CustomerNumber', request_data.credentials.customer_number),
            ('SecurityCode', request_data.credentials.security_code)
        ]))
    ])
    request_dict = OrderedDict([
        ('CNConsumerRequests', OrderedDict([
            ('CNConsumerRequest', OrderedDict([
                ('Subjects', OrderedDict([
                    ('Subject', OrderedDict([
                        ('@subjectType', 'SUBJ'),
                        ('SubjectName', OrderedDict([
                            ('LastName', request_data.input_data.last_name),
                            ('FirstName', request_data.input_data.first_name)
                        ])),
                        ('DateOfBirth', request_data.input_data.dob)
                    ])),
                    ('Addresses', OrderedDict([
                        ('Address', request_data.input_data.address_history.current.as_equifax_address())
                    ]))
                ]))  # May need to also send ('CreditFileRequest', 0) once Dual Source is configured
            ]))
        ]))
    ])
    root['CNCustTransmitToEfx'] = OrderedDict([
        ('CNCustomerInfo', auth_dict),
        ('CNRequests', request_dict),
    ])
    return unparse(root)


def process_equifax_response(raw_response):
    try:
        response = dict(parse(raw_response))
        response_model = EquifaxResponseWithRoot.from_json(response)

        return {
            'output_data': response_model.root.efx_report.get_ekyc_result() if response_model.root.efx_report else None,
            'errors': response_model.get_errors()
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
