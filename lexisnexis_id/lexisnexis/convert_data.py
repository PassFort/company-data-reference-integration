def passfort_to_lexisnexis_data(passfort_data):
    lexisnexis_pkg = {
        "InstantIDRequest": {
            "User": {
                "GLBPurpose": "5",
                "DLPurpose": "3"
            },
            "Options": {
                "IncludeModels": {
                    "FraudPointModel": {
                        "IncludeRiskIndices": True
                    }
                },
                "DOBMatch": {
                    "MatchType": "FuzzyCCYYMMDD"
                },
                "NameInputOrder": "Unknown"
            },
            "SearchBy": {
            }
        }
    }

    if passfort_data.get('input_data'):
        # Check Personal details 
        if passfort_data['input_data'].get('personal_details'):
            # Check name
            if passfort_data['input_data']['personal_details'].get('name'):
                given_names = passfort_data['input_data']['personal_details']['name'].get('given_names')
                name = {}

                if given_names:
                    name['First'] = given_names[0]
                    if given_names[1:]:
                        name['Middle'] = ' '.join(given_names[1:])
                if passfort_data['input_data']['personal_details']['name'].get('family_name'):
                    name['Last'] = passfort_data['input_data']['personal_details']['name']['family_name']

                lexisnexis_pkg['InstantIDRequest']['SearchBy']['Name'] = name

            # Check date of birthday
            if passfort_data['input_data']['personal_details'].get('dob'):
                date_of_birth = passfort_data['input_data']['personal_details']['dob'].split('-')
                date_of_birth_options = ['Year', 'Month', 'Day']
                dob = {}

                for index, part_of_date in enumerate(date_of_birth):
                    dob[date_of_birth_options[index]] = int(part_of_date)

                lexisnexis_pkg['InstantIDRequest']['SearchBy']['DOB'] = dob

            # Check gender
            if passfort_data['input_data']['personal_details'].get('gender'):
                lexisnexis_pkg['InstantIDRequest']['SearchBy']['Gender'] = \
                    passfort_data['input_data']['personal_details']['gender'].upper()

            #  Check SSN ( Soßcial Security Number )
            if passfort_data['input_data']['personal_details'].get('national_identity_number'):
                nin_raw = passfort_data['input_data']['personal_details']['national_identity_number']
                nin_numbers = ''.join(filter(str.isdigit, nin_raw))
                if nin_numbers:
                    lexisnexis_pkg['InstantIDRequest']['SearchBy']['SSN'] = nin_numbers

        # Check address - Just the last address history
        if passfort_data['input_data'].get('address_history'):
            for idx, address in enumerate(passfort_data['input_data']['address_history'][:1]):
                address_to_check = address['address']

                address = {}

                #  START Building street address prop
                if address_to_check.get('street_number'):
                    address['StreetAddress1'] = address.get('StreetAddress1', '') + ' ' + str(
                        address_to_check['street_number'])

                if address_to_check.get('route'):
                    address['StreetAddress1'] = address.get('StreetAddress1', '') + ' ' + str(address_to_check['route'])

                if address_to_check.get('premise'):
                    address['StreetAddress1'] = address.get('StreetAddress1', '') + ' ' + str(
                        address_to_check['premise'])

                if address_to_check.get('subpremise'):
                    address['StreetAddress1'] = address.get('StreetAddress1', '') + ' ' + str(
                        address_to_check['subpremise'])

                # remove blank spaces
                if address.get('StreetAddress1'):
                    address['StreetAddress1'] = address['StreetAddress1'].strip()
                #  END Building street address prop

                if address_to_check.get('postal_town'):
                    address['City'] = address_to_check['postal_town']

                if address_to_check.get('state_province'):
                    address['State'] = address_to_check['state_province']

                if address_to_check.get('postal_code'):
                    address['Zip5'] = address_to_check['postal_code']

                if address:
                    lexisnexis_pkg['InstantIDRequest']['SearchBy']['Address'] = address

        # Check Communication
        if passfort_data['input_data'].get('contact_details'):
            if passfort_data['input_data']['contact_details'].get('email'):
                lexisnexis_pkg['InstantIDRequest']['SearchBy']['Email'] = \
                    passfort_data['input_data']['contact_details']['email']

            if passfort_data['input_data']['contact_details'].get('phone_number'):
                lexisnexis_pkg['InstantIDRequest']['SearchBy']['HomePhone'] = \
                    passfort_data['input_data']['contact_details']['phone_number']
                lexisnexis_pkg['InstantIDRequest']['SearchBy']['WorkPhone'] = \
                    passfort_data['input_data']['contact_details']['phone_number']

    return lexisnexis_pkg


def lexisnexis_to_passfort_data(lexisnexis_response_data):
    # base response
    response_body = {
        "output_data": {
            "decision": 'FAIL'
        },
        "raw": lexisnexis_response_data.get('body'),
        "errors": []
    }

    if lexisnexis_response_data['status'] in [401, 403]:
        response_body['errors'].append({
            'code': 302,
            'message': 'Provider Error: IP address that is not on the white list or invalid credentials'})
        response_body['output_data']['decision'] = 'ERROR'

    elif lexisnexis_response_data['status'] in [408, 504]:
        response_body['errors'].append({
            'code': 403,
            'message': 'Provider Error: TIMEOUT'})
        response_body['output_data']['decision'] = 'ERROR'

    elif lexisnexis_response_data['status'] > 400:
        response_body['errors'].append({
            'code': 303,
            'message': f"Provider Error: UNKNOWN ERROR: {lexisnexis_response_data['body']}"})
        response_body['output_data']['decision'] = 'ERROR'

    elif lexisnexis_response_data['status'] == 200:
        lexisnexis_data = lexisnexis_response_data['body']
        if lexisnexis_data and \
                'InstantIDResponseEx' in lexisnexis_data and \
                'response' in lexisnexis_data['InstantIDResponseEx'] and \
                'Result' in lexisnexis_data['InstantIDResponseEx']['response'] and \
                'VerifiedInput' in lexisnexis_data['InstantIDResponseEx']['response']['Result']:

            verified_input = lexisnexis_data['InstantIDResponseEx']['response']['Result']['VerifiedInput']
            match = {
                'database_name': 'LexisNexis DB',
                'database_type': 'CIVIL',
                'matched_fields': []
            }
            # check names
            if verified_input.get('Name'):
                # check forename
                if verified_input['Name'].get('First'):
                    match['matched_fields'].append('FORENAME')
                # check surname
                if verified_input['Name'].get('Last'):
                    match['matched_fields'].append('SURNAME')

            # check date of birthday (DOB)
            if 'DOB' in lexisnexis_data['InstantIDResponseEx']['response']['Result']['InputEcho']:
                input_dob = lexisnexis_data['InstantIDResponseEx']['response']['Result']['InputEcho']['DOB'].keys()
                verified_dob = verified_input['DOB'].keys()

                # If all part of the input date is in the verified date, added DOB verification
                if not next(filter(lambda k: k not in verified_dob, input_dob), None):
                    match['matched_fields'].append('DOB')

            # check address
            if verified_input.get('Address'):
                match['matched_fields'].append('ADDRESS')

            # Update decision
            if match['matched_fields']:
                response_body['output_data']['decision'] = 'PASS'

            response_body['output_data']["entity_type"] = "INDIVIDUAL"
            response_body['output_data']["electronic_id_check"] = {"matches": [match]}

    # Check global errors
    # check_errors(lexisnexis_data, response_body)

    return response_body


def check_errors(error_section, response_body):
    # Check errors:
    pass
