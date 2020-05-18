import os
import json
import requests

from base64 import b64encode


def echo_test_request(credentials):
    headers = {'Content-Type': 'application/json'}

    request_body = {
        'credentials': {
            'username': credentials['username'],
            'password': credentials['password'],
            'tenant': credentials['tenant'],
        },
    }

    url = credentials['url']

    response = requests.post(
        url = url, 
        headers=headers,
        # GDC expects auth credentials as an object on payload
        data=json.dumps(request_body))

    print(response.status_code)                         

    return response.status_code

def verify(request_body, credentials):
    
    # TODO complete request 

    headers = {'Content-Type': 'application/json'}
    url = credentials['url']
    
    auth = {
        'credentials': {
            'username': credentials['username'],
            'password': credentials['password'],
            'tenant': credentials['tenant'],
        }
    }

    # for GDC we also need to pass those extra options
    query_options = credentials.get('options')
    
    options = { 'options': query_options } if query_options else {}

    response = requests.post(
        url = url,
        headers=headers,
        # GDC expects auth credentials as an object on payload
        data=json.dumps({**request_body, **auth, **options}))

    return {
        'status': response.status_code, 
        'body': response.json() if response.status_code == 200 else response.text 
    }
    
