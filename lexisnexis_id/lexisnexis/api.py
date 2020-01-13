import os
import json
import requests

def echo_test_request(credentials):
    request_proxy = os.getenv('REQUEST_PROXY')
    headers = {'Content-Type': 'application/json'}
    url = credentials['url'] + "/WsIdentity/EchoTest"
    proxies = {'http': request_proxy, 'https': request_proxy}

    data = {
        'EchoTestRequest': {
            'ValueIn': 'Connection test'
        }
    }
    
    response = requests.post(
        url, 
        headers=headers,
        auth=(credentials['username'], credentials['password']), 
        proxies=proxies,
        data=json.dumps(data))

    return response.status_code

def verify(request_body, credentials):
    request_proxy = os.getenv('REQUEST_PROXY')
    headers = {'Content-Type': 'application/json'}
    url = credentials['url'] + "/WsIdentity/InstantID"
    proxies = {'http': request_proxy, 'https': request_proxy}
     
    response = requests.post(
        url = url,
        headers=headers, 
        auth=(credentials['username'], credentials['password']), 
        proxies=proxies, 
        data=json.dumps(request_body))

    return {
        'status': response.status_code, 
        'body': response.json() if response.status_code == 200 else response.text 
    }
    
