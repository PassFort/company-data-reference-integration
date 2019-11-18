import json
import requests

def validate_authentication(user, password):
    url = "https://api.globaldatacompany.com/connection/v1/testauthentication"
    response = requests.get(url, auth=(user, password))

    return response.status_code

def verify(user, password, country_code, data_fields):
    headers = {'Content-Type': 'application/json'}
    url = 'https://api.globaldatacompany.com/verifications/v1/verify'

    base_body = {
        "AcceptTruliooTermsAndConditions": True, 
        "CleansedAddress": False, 
        "ConfigurationName": "Identity Verification", 
        "CountryCode": country_code, 
        "DataFields": data_fields, 
        "VerboseMode": False
    }

    #Check consents and add to a body
    consents_for_data_sources = consents(user, password, country_code)
    if consents_for_data_sources:
        base_body['ConsentForDataSources'] = consents_for_data_sources

    response = requests.post(
        url, 
        auth=(user, password), 
        data=json.dumps(base_body), 
        headers=headers)

    response.raise_for_status()
    return response.json()

def consents(user, password, country_code):
    headers = {'Content-Type': 'application/json'}
    url = f'https://api.globaldatacompany.com/configuration/v1/consents/Identity%20Verification/{country_code}'

    response = requests.get(
        url, 
        auth=(user, password),  
        headers=headers)

    if response.status_code == 200:
        return response.json()
    else:
        return []
