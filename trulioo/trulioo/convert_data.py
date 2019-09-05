import pycountry

def passfort_to_trulioo_data(passfort_data):
    
    trulioo_pkg = {}
    country_code = 'GB' #Default


    if passfort_data.get('input_data'):
        #Check Personal details 
        if passfort_data['input_data'].get('personal_details'):
            trulioo_pkg['PersonInfo'] = {}

            #Check name
            if passfort_data['input_data']['personal_details'].get('name'):
                if passfort_data['input_data']['personal_details']['name'].get('given_names'):
                    given_names = passfort_data['input_data']['personal_details']['name']['given_names']
                    
                    trulioo_pkg['PersonInfo']['FirstGivenName'] = given_names[0]

                    if given_names[1:]:
                        trulioo_pkg['PersonInfo']['MiddleName'] = ' '.join(given_names[1:])

                if passfort_data['input_data']['personal_details']['name'].get('family_name'):
                    trulioo_pkg['PersonInfo']['FirstSurName'] = passfort_data['input_data']['personal_details']['name']['family_name']

            #Check date of birthday
            if passfort_data['input_data']['personal_details'].get('dob'):
                date_of_birth = passfort_data['input_data']['personal_details']['dob'].split('-')

                date_of_birth_options = ['YearOfBirth', 'MonthOfBirth', 'DayOfBirth']

                for index, part_of_date in enumerate(date_of_birth):
                    trulioo_pkg['PersonInfo'][date_of_birth_options[index]] = int(part_of_date)

            #Check gender
            if passfort_data['input_data']['personal_details'].get('gender'):
                trulioo_pkg['PersonInfo']['Gender'] = passfort_data['input_data']['personal_details']['gender']


        #Check address
        if passfort_data['input_data'].get('address_history'):
            if passfort_data['input_data']['address_history'].get('current'):
                address_to_check = passfort_data['input_data']['address_history']['current']

                trulioo_pkg['Location'] = {}
               
                if address_to_check.get('street_number'):
                    trulioo_pkg['Location']['BuildingNumber'] = address_to_check['street_number']

                if address_to_check.get('premise'):
                    trulioo_pkg['Location']['BuildingName'] = address_to_check['premise']

                if address_to_check.get('subpremise'):
                    trulioo_pkg['Location']['UnitNumber'] = address_to_check['subpremise']

                if address_to_check.get('route'):
                    trulioo_pkg['Location']['StreetName'] = address_to_check['route']

                if address_to_check.get('postal_town'):
                    trulioo_pkg['Location']['City'] = address_to_check['postal_town']

                if address_to_check.get('locality'):
                    trulioo_pkg['Location']['Suburb'] = address_to_check['locality']

                if address_to_check.get('county'):
                    trulioo_pkg['Location']['County'] = address_to_check['county']        

                if address_to_check.get('state_province'):
                    trulioo_pkg['Location']['StateProvinceCode'] = address_to_check['state_province']

                if address_to_check.get('postal_code'):
                    trulioo_pkg['Location']['PostalCode'] = address_to_check['postal_code']

                if address_to_check.get('country'):
                    #Convert the country code from 3 to 2 alpha ( like "GBR" to "GB")
                    country = pycountry.countries.get(alpha_3=address_to_check['country'])
                    country_code = country.alpha_2
            
        #Check Communication
        if passfort_data['input_data'].get('contact_details'):
            trulioo_pkg['Communication'] = {}

            if passfort_data['input_data']['contact_details'].get('email'):
                trulioo_pkg['Communication']['EmailAddress'] = passfort_data['input_data']['contact_details']['email']

            if passfort_data['input_data']['contact_details'].get('phone_number'):
                trulioo_pkg['Communication']['Telephone'] = passfort_data['input_data']['contact_details']['phone_number']

    return trulioo_pkg, country_code


def trulioo_to_passfort_data(trulioo_data):
    #base response
    response_body = {
        "output_data": {
        },
        "raw": trulioo_data,
        "errors": []
    }

    #Check global errors
    check_errors(trulioo_data, response_body)
            
    if trulioo_data.get('Record') and trulioo_data['Record'].get('DatasourceResults'):
        matches = []

        for datasource in trulioo_data['Record']['DatasourceResults']:

            #Check datasource errors
            check_errors(datasource, response_body)

            match = {
                'database_name': datasource['DatasourceName'],
                'database_type': 'CREDIT' if 'credit' in datasource['DatasourceName'].lower() else 'CIVIL',
                'matched_fields': []
            }

            if datasource.get('DatasourceFields'):
                #check forename
                forename_field = next((field for field in datasource['DatasourceFields'] if field["FieldName"] == "FirstGivenName"), None)
                if forename_field and forename_field['Status'] == 'match':
                    match['matched_fields'].append('FORENAME')

                #check surname
                surname_field = next((field for field in datasource['DatasourceFields'] if field["FieldName"] == "FirstSurName"), None)
                if surname_field and surname_field['Status'] == 'match':
                    match['matched_fields'].append('SURNAME')

                #check date of birthday (DOB)
                dob_fields = []
                for dob_field in ['DayOfBirth', 'MonthOfBirth', 'YearOfBirth']:
                    dob_field_check = next((field for field in datasource['DatasourceFields'] if field["FieldName"] == dob_field), None)
                    if dob_field_check:
                        dob_fields.append(dob_field_check)

                #If all the fiels belonging to dob found in the datasource filds are with match status
                if dob_fields and (not next((field for field in dob_fields if field["Status"] == "nomatch"), False)):
                    match['matched_fields'].append('DOB')

                ## TODO - ADDRESS

                address_fields = []
                for address_field in [  'BuildingNumber', 
                                        'BuildingName', 
                                        'UnitNumber', 
                                        'StreetName', 
                                        'City', 
                                        'Suburb', 
                                        'County', 
                                        'StateProvinceCode', 
                                        'PostalCode']:
                    address_field_check = next((field for field in datasource['DatasourceFields'] if field["FieldName"] == address_field), None)
                    if address_field_check:
                        address_fields.append(address_field_check)
                #If all the fiels belonging to address found in the datasource filds are with match status
                if address_fields and (not next((field for field in address_fields if field["Status"] == "nomatch"), False)):
                    match['matched_fields'].append('ADDRESS')

                #if have matches add
                if match['matched_fields']:
                    matches.append(match)

        if matches:
            response_body['output_data']["entity_type"] = "INDIVIDUAL"
            response_body['output_data']["electronic_id_check"] = {"matches": matches}

    return response_body

def check_errors(error_section, response_body):
    #Check errors:
    for error in error_section.get('Errors', []):
        if error.get('Code') in ['InternalServerError', '2000']:
            response_body['errors'].append({'code': 401, 'message': 'Unknown internal error'})
        
        elif error.get('Code') in ['1001', '4001', '3005'] and\
                not next((error for error in response_body['errors'] if error['code'] == 101), None):
            response_body['errors'].append({'code': 101, 'message': 'Missing required fields'})
        
        elif error.get('Code') in ['1006', '1008'] and\
                not next((error for error in response_body['errors'] if error['code'] == 201), None):
            response_body['errors'].append({
                'code': 201,
                'message': f'The submitted data was invalid. Provider returned error code {error.get("Code")}'
            })