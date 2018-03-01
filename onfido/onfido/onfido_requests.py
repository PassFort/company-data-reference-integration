import requests
from simplejson.errors import JSONDecodeError
import logging


def make_onfido_requestor(apikey):
    def onfido_request(method, url, **kwargs):
        if not (url.startswith('https://api')):
            url = 'https://api.onfido.com/v2/' + url
        response = requests.request(method,
                                    url,
                                    headers={'Authorization': 'Token token=' + apikey},
                                    **kwargs,
                                    )
        try:
            content = response.json()
        except JSONDecodeError:
            return 500, "Server returned {!r} with no content.".format(response.status_code)

        return response.status_code, content

    return onfido_request


def create_identity_check(requestor, applicant_id):
    logging.info('create a check')

    check = {
        'type': 'express',
        'reports': [{"name": "identity", "variant": "kyc"}],
    }
    status, create_identity_response = requestor('POST',
                                                 'applicants/' + applicant_id + '/checks',
                                                 json=check,
                                                 )
    return status, create_identity_response


def passfort_to_onfido_address(passfort_address):
    structured_address = passfort_address.get('original_structured_address')
    if structured_address is None:
        return None
    address = {}
    address['flat_number'] = structured_address.get('subpremise')
    address['building_number'] = structured_address.get('street_number')
    address['town'] = structured_address.get('locality')
    address['street'] = structured_address.get('route')
    address['postcode'] = structured_address.get('postal_code')
    address['country'] = structured_address.get('country')
    address['state'] = structured_address.get('state_province')
    address['building_name'] = structured_address.get('premise')
    return dict((k, v) for k, v in address.items() if v)


def create_applicant(requestor, input_data):
    logging.info('create applicant')
    # convert PF data structure to onfido applicant
    applicant = {}
    given_names = input_data['personal_details']['name']['v']['given_names']
    applicant['first_name'] = given_names[0]
    applicant['last_name'] = input_data['personal_details']['name']['v']['family_name']
    applicant['middle_name'] = " ".join(given_names[1:len(given_names)])
    applicant['dob'] = input_data['personal_details']['dob']['v']
    if input_data['personal_details'].get('nationality ') is not None:
        applicant['nationality'] = input_data['personal_details']['nationality']['v']
    if input_data['address_history'].get('current', {}).get('country', {}):
        applicant['country'] = input_data['address_history']['current']['country']
    applicant['addresses'] = list(filter(None, [
        passfort_to_onfido_address(input_data['address_history']['current'])]))

    status, create_applicant_response = requestor('POST', 'applicants',
                                                  json=applicant,
                                                  )
    return status, create_applicant_response

