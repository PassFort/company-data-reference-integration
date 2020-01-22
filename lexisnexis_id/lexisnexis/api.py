import os
import json
import requests


def echo_test_request(credentials):
    headers = {'Content-Type': 'application/json'}
    url = credentials['url'] + "/WsIdentity/EchoTest"

    data = {
        'EchoTestRequest': {
            'ValueIn': 'Connection test'
        }
    }

    response = requests.post(
        url,
        headers=headers,
        auth=(credentials['username'], credentials['password']),
        data=json.dumps(data))

    return response.status_code


def verify(request_body, credentials):
    headers = {'Content-Type': 'application/json'}
    url = credentials['url'] + "/WsIdentity/InstantID"

    response = requests.post(
        url=url,
        headers=headers,
        auth=(credentials['username'], credentials['password']),
        data=json.dumps(request_body))

    return {
        'status': response.status_code,
        'body': response.json() if response.status_code == 200 else response.text
    }
