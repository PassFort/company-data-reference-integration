import os
import json
import requests

from base64 import b64encode


def echo_test_request(credentials):
    headers = {'Content-Type': 'application/json'}
    url = credentials['url'] + f"?profileShortCode={credentials['profile_short_code']}"
    
    response = requests.get(
        url, 
        headers=headers,
        auth=(credentials['license_key'], credentials['client_key']))

    return response.status_code

def verify(request_body, credentials):
    headers = {'Content-Type': 'application/json'}
    url = credentials['url'] + f"?profileShortCode={credentials['profile_short_code']}"
     
    response = requests.post(
        url = url,
        headers=headers, 
        auth=(credentials['license_key'], credentials['client_key']), 
        data=json.dumps(request_body))

    return {
        'status': response.status_code, 
        'body': response.json() if response.status_code == 200 else response.text 
    }
    
