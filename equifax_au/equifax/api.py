import json
import requests
import logging

from equifax.convert_data import xml_to_dict_response, passfort_to_equifax_ping

def echo_test_request(request_data, url):

    request_body = passfort_to_equifax_ping(request_data)

    headers = {'Content-Type': 'text/xml; charset=utf-8'}
    url = url + '/sys2/ping-v1'
    response = requests.post(
        url,
        data=request_body,
        headers=headers)

    if response.status_code != 200:
        response_body = xml_to_dict_response(response.text)
        if 'soapenv:Fault' in response_body:
            server_fault = response_body['soapenv:Fault']['detail']['l7:policyResult']['@status']
            logging.error(server_fault)
            if server_fault == 'Authentication Failed':
                return 'MISCONFIGURATION_ERROR', 205
            else:
                return 'PROVIDER_UNKNOWN_ERROR', 301

    return "Equifax Integration", response.status_code

def verify(request_body, base_url):
    headers = {'Content-Type': 'text/xml; charset=utf-8'}
    url = base_url + '/sys2/idmatrix-v4'

    response = requests.post(
        url,
        data=request_body,
        headers=headers)

    return response.text
