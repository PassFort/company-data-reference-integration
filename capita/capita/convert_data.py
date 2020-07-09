EU_ID_CARD_COUNTRY_CODES = [
    'AUT', 'HRV', 'CYP', 'CZE',
    'EST', 'FIN', 'FRA', 'DEU',
    'GRC', 'HUN', 'IRL', 'LVA',
    'LTU', 'LUX', 'MLT', 'NLD',
    'POL', 'PRT', 'ROU', 'SVK',
    'SVN', 'ESP', None
]


def passfort_to_capita_data(passfort_data):
    
    capita_pkg  = {}

    if passfort_data.get('input_data'):
        person = {}
        #Check Personal details 
        if passfort_data['input_data'].get('personal_details'):
            #Check name
            if passfort_data['input_data']['personal_details'].get('name'):
                given_names =  passfort_data['input_data']['personal_details']['name'].get('given_names')
                
                if given_names:
                    person['Forename'] = given_names[0]
                    if given_names[1:]:
                        person['Secondname'] = ' '.join(given_names[1:])
                if passfort_data['input_data']['personal_details']['name'].get('family_name'):
                    person['Surname'] = passfort_data['input_data']['personal_details']['name']['family_name']
                
            #Check date of birthday
            if passfort_data['input_data']['personal_details'].get('dob'):
                date_of_birth = passfort_data['input_data']['personal_details']['dob']
                    
                person['Date_Of_Birth'] = date_of_birth
        
            # Check Personal Number
            if passfort_data['input_data']['personal_details'].get('national_identity_number'):
                personal_number = passfort_data['input_data']['personal_details']['national_identity_number']
                person['PersonalNumber'] = personal_number
            
            #Check gender
            if passfort_data['input_data']['personal_details'].get('gender'):
                person['Gender'] = passfort_data['input_data']['personal_details']['gender'].upper()

            capita_pkg['Person'] = person

        #Check address
        if passfort_data['input_data'].get('address_history'):
            for address in passfort_data['input_data']['address_history']:
                address_to_check = address['address']

                address = {}

                if address_to_check.get('premise'):
                    address['HouseName'] = address_to_check['premise']

                if address_to_check.get('subpremise'):
                    address['HouseNumber'] = address_to_check['subpremise']

                if address_to_check.get('postal_town'):
                    address['PostTown'] = address_to_check['postal_town']

                if address_to_check.get('locality'):
                    address['District'] = address_to_check['locality']

                if address_to_check.get('county'):
                    address['County'] = address_to_check['county']        

                if address_to_check.get('postal_code'):
                    address['PostCode'] = address_to_check['postal_code']

                if address:
                    if 'Address' not in capita_pkg:
                        capita_pkg['Address'] = []

                    capita_pkg['Address'].append(address)

        licence = next(
            (doc for doc
             in passfort_data['input_data'].get('documents_metadata', [])
             if doc['document_type'] == 'DRIVING_LICENCE' and doc.get('country_code') in ('GBR', None))
            , None
        )
        if licence and licence.get('number'):
            capita_pkg['DriverLicenceNo'] = licence['number']

        id_card = next(
            (doc for doc
             in passfort_data['input_data'].get('documents_metadata', [])
             if doc['document_type'] == 'STATE_ID' and doc.get('country_code') in EU_ID_CARD_COUNTRY_CODES)
            , None
        )
        if id_card and id_card.get('number'):
            capita_pkg['EuropeanIDCardNo'] = id_card['number']

    return capita_pkg


def get_database_type(check_name):
    if 'credit' in check_name:
        return 'CREDIT'
    if 'death register' in check_name:
        return 'MORTALITY'
    return 'CIVIL'


def capita_to_passfort_data(capita_response_data):
    #base response
    response_body = {
        "output_data": {
            "decision": 'FAIL',
            "entity_type": "INDIVIDUAL",
            "electronic_id_check": {"matches": []}
        },
        "raw": capita_response_data.get('body'),
        "errors": []
    }

    # if capita_response_data['status'] in [401, 403]:
    #     response_body['errors'].append({
    #             'code': 302, 
    #             'message': 'Provider Error: IP address that is not on the white list or invalid credentials'})
    #     response_body['output_data']['decision'] = 'ERROR'

    # elif capita_response_data['status'] in [408, 504]:
    #     response_body['errors'].append({
    #         'code': 403, 
    #         'message': 'Provider Error: TIMEOUT'})
    #     response_body['output_data']['decision'] = 'ERROR'

    if capita_response_data['status'] > 400:          
        response_body['errors'].append({
                'code': 303, 
                'message': f"Provider Error: UNKNOWN ERROR: {capita_response_data['body']}"})
        response_body['output_data']['decision'] = 'ERROR'
    
    
    if capita_response_data['status'] == 200:
        capita_data = capita_response_data['body']
        if capita_data:
            about = capita_data.get('About')
            if about:
                response_body['output_data']['electronic_id_check']['provider_reference_number'] = about.get('TransactionReference')
            if 'Response' in capita_data and\
                'Result' in capita_data['Response']:
                
                results = capita_data['Response']['Result']
                
                if capita_data['Response'].get('Error'):
                    response_body['output_data']['decision'] = 'ERROR'
                    
                    error_code = capita_data['Response']['Error']

                    error_list  = {
                        "10101001": "Supplier Info for Address Check not Found.",
                        "10101000": "Error in Executing Request.",
                        "10100200": "Error Authenticating Client Request.",
                        "10100201": "Request Raised from Unknown Host.",
                        "10100202": "Invalid Licence used.",
                        "10100203": "Web Licence not authorized for API call.",
                        "10100300": "Error Authorizing Client Request.",
                        "10100301": "Transaction has been blocked.",
                        "10100302": "Required credentials are missing for the request.",
                        "10100303": "Profile not valid for Licence used.",
                        "10100401": "Please validate Applicant Detail, mandatory field missing.",
                        "10100400": "Error Validating Client Request.",
                        "10110200": "Please validate Client Key.",
                        "10110100": "Please validate Profile Shortcode.",
                        "10140101": "Please validate Applicant Detail, mandatory field missing."
                    }

                    if error_code in [
                            "10100200",
                            "10100202",
                            "10100302",
                            "10100303",
                            "10110200",
                            "10110100"
                        ]:
                        response_body['errors'].append({
                                'code': 302, 
                                'message': f'Provider Error: {error_list[error_code]}'})

                    elif error_code in [
                            "10100401",
                            "10140101"
                        ]:
                        response_body['errors'].append({
                            'code': 101, 
                            'message': f'Provider Error: {error_list[error_code]}'})

                    elif error_list.get(error_code):          
                        response_body['errors'].append({
                                'code': 303, 
                                'message': f'Provider Error: {error_list[error_code]}'})

                else:
                    try:
                        stage_1 = next(filter(lambda x: x['Name'] == 'Stage1', results))
                        has_mortality_match = False
                        if 'CheckResults' in stage_1:
                            for result in stage_1['CheckResults']:

                                database_name = result['CheckName'].split('(')[0].strip()
                                try:
                                    match = next(filter(lambda m: m['database_name'] == database_name, 
                                            response_body['output_data']['electronic_id_check']['matches']))
                                except StopIteration:
                                    match = {
                                        'database_name': result['CheckName'].split('(')[0].strip(),
                                        'database_type': get_database_type(result['CheckName'].lower()),
                                        'matched_fields': []
                                    }
                                    response_body['output_data']['electronic_id_check']['matches'].append(match)

                                if result['Result'] == 1:
                                    #Default values for match
                                    if 'FORENAME' not in match['matched_fields']:
                                        match['matched_fields'].append('FORENAME')
                                    if 'SURNAME' not in match['matched_fields']:
                                        match['matched_fields'].append('SURNAME')

                                    #Update decision
                                    if match['database_type'] == 'MORTALITY':
                                        has_mortality_match = True
                                        match['matched_fields'].append('DOB')

                                    if not has_mortality_match and \
                                            response_body['output_data']['decision'] == 'FAIL':
                                        response_body['output_data']['decision'] = 'PASS'

                                    #Database check
                                    if 'Proof of DOB' in result['CheckName']:
                                        match['matched_fields'].append('DOB')
                                    elif 'Proof of Address' in result['CheckName']:
                                        match['matched_fields'].append('ADDRESS')

                                if result['Error']:
                                    #Check to not add twice the same error
                                    error_message = f"Provider Error: UNKNOWN ERROR: {result['Error']}"
                                    try:
                                        next(filter(lambda error: error['message'] == error_message, 
                                            response_body['errors']))
                                    except StopIteration: 
                                        response_body['errors'].append({
                                            'code': 303, 
                                            'message': error_message}) 

                    except StopIteration:
                        response_body['errors'].append({
                            'code': 303, 
                            'message': f"Provider Error: Stage 1 section not found"})

    return response_body
