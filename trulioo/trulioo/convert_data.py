from datetime import datetime
import pycountry

basic_components = {
    'StreetName',
    'PostalCode',
}

valid_address_combinations = [
    {
        *basic_components,
        'BuildingName',
    },
    {
        *basic_components,
        'BuildingNumber',
    },
]


def is_full_address(components):
    return any((
        components.issuperset(valid_combination)
        for valid_combination in valid_address_combinations
    ))


def get_national_id_type(country_code, number):
    if country_code == 'GBR':
        return 'Health' if len(number) == 10 else 'SocialService'
    if country_code == 'IND':
        return 'SocialService' if len(number) == 10 else 'NationalID'
    if country_code == 'MEX':
        return 'SocialService' if len(number) in (12, 13) else 'NationalID'
    if country_code == 'AUS':
        return 'Health' if len(number) == 11 else 'SocialService'
    if country_code == 'RUS':
        return 'TaxIDNumber' if len(number) == 12 else 'SocialService'

    if country_code in [
        'CHN',
        'FIN',
        'FRA',
        'HKG',
        'MYS',
        'SGP',
        'SWE',
        'ESP',
        'TUR',
    ]:
        return 'NationalID'

    if country_code in [
        'CAN',
        'IRL',
        'ITA',
        'USA'
    ]:
        return 'SocialService'

    return 'NationalID'


def passfort_to_trulioo_data(passfort_data):
    trulioo_pkg = {}
    country = pycountry.countries.get(alpha_3='GBR') # Default

    if passfort_data.get('input_data'):
        # Check Personal details
        personal_details = passfort_data['input_data'].get('personal_details')
        if personal_details:
            trulioo_pkg['PersonInfo'] = {}

            national_id = personal_details.get('national_identity_number')
            if national_id:
                trulioo_pkg['NationalIds'] = [
                    {
                        'Type': get_national_id_type(country_code, number),
                        'Number': number,
                    } for country_code, number in national_id.items()
                ]

            # Check name
            if personal_details.get('name'):
                if personal_details['name'].get('given_names'):
                    given_names = personal_details['name']['given_names']

                    trulioo_pkg['PersonInfo']['FirstGivenName'] = given_names[0]

                    if given_names[1:]:
                        trulioo_pkg['PersonInfo']['MiddleName'] = ' '.join(
                            given_names[1:])

                if personal_details['name'].get('family_name'):
                    trulioo_pkg['PersonInfo']['FirstSurName'] = personal_details['name']['family_name']

            # Check date of birthday
            if personal_details.get('dob'):
                date_of_birth = personal_details['dob'].split('-')

                date_of_birth_options = [
                    'YearOfBirth', 'MonthOfBirth', 'DayOfBirth']

                for index, part_of_date in enumerate(date_of_birth):
                    trulioo_pkg['PersonInfo'][date_of_birth_options[index]] = int(
                        part_of_date)

            # Check gender
            if personal_details.get('gender'):
                trulioo_pkg['PersonInfo']['Gender'] = personal_details['gender']

        # Check address
        if passfort_data['input_data'].get('address_history'):
            address_to_check = passfort_data['input_data']['address_history'][0]['address']
            trulioo_pkg['Location'] = {}

            if address_to_check.get('street_number'):
                trulioo_pkg['Location']['BuildingNumber'] = address_to_check['street_number']

            if address_to_check.get('premise'):
                trulioo_pkg['Location']['BuildingName'] = address_to_check['premise']

            if address_to_check.get('subpremise'):
                trulioo_pkg['Location']['UnitNumber'] = address_to_check['subpremise']

            if address_to_check.get('route'):
                trulioo_pkg['Location']['StreetName'] = address_to_check['route']

            locality = address_to_check.get('locality')
            postal_town = address_to_check.get('postal_town')
            city = locality or postal_town
            if city:
                trulioo_pkg['Location']['City'] = city

            if locality and postal_town:
                trulioo_pkg['Location']['Suburb'] = postal_town

            if address_to_check.get('county'):
                trulioo_pkg['Location']['County'] = address_to_check['county']

            if address_to_check.get('state_province'):
                trulioo_pkg['Location']['StateProvinceCode'] = address_to_check['state_province']

            if address_to_check.get('postal_code'):
                trulioo_pkg['Location']['PostalCode'] = address_to_check['postal_code']

            if address_to_check.get('country'):
                # Convert the country code from 3 to 2 alpha ( like "GBR" to "GB")
                country = pycountry.countries.get(
                    alpha_3=address_to_check['country'])

        # Check Communication
        if passfort_data['input_data'].get('contact_details'):
            trulioo_pkg['Communication'] = {}

            if passfort_data['input_data']['contact_details'].get('email'):
                trulioo_pkg['Communication']['EmailAddress'] = passfort_data['input_data']['contact_details']['email']

            if passfort_data['input_data']['contact_details'].get('phone_number'):
                trulioo_pkg['Communication']['Telephone'] = passfort_data['input_data']['contact_details']['phone_number']

        # Driving licence
        licence = next(
            (doc for doc
             in passfort_data['input_data'].get('documents_metadata', [])
             if doc['document_type'] == 'DRIVING_LICENCE' and doc['country_code'] == country.alpha_3)
            , None
        )
        if licence and licence['number']:
            trulioo_pkg['DriverLicence'] = {'Number': licence['number']}
            if licence['issuing_state']:
                trulioo_pkg['DriverLicence']['State'] = licence['issuing_state']

    return trulioo_pkg, country.alpha_2


def trulioo_to_passfort_data(trulioo_request, trulioo_data):
    trulioo_record = trulioo_data.get('Record', {})
    errors = trulioo_to_passfort_errors(trulioo_data.get('Errors', []))
    if trulioo_record.get('RecordStatus') == 'match':
        decision = 'PASS'
    elif errors:
        decision = 'ERROR'
    else:
        decision = 'FAIL'

    response_body = {
        'decision': decision,
        'output_data': {},
        'raw': trulioo_data,
        'errors': errors,
    }

    matches = []
    for datasource in trulioo_record.get('DatasourceResults', []):
        match = {
            'database_name': datasource['DatasourceName'],
            'database_type': 'CREDIT' if 'credit' in datasource['DatasourceName'].lower() else 'CIVIL',
            'matched_fields': [],
        }

        if datasource.get('DatasourceFields'):
            # check forename
            forename_field = next(
                (field for field in datasource['DatasourceFields'] if field["FieldName"] == "FirstGivenName"), None)
            if forename_field and forename_field['Status'] == 'match':
                match['matched_fields'].append('FORENAME')

            # check surname
            surname_field = next(
                (field for field in datasource['DatasourceFields'] if field["FieldName"] == "FirstSurName"), None)
            if surname_field and surname_field['Status'] == 'match':
                match['matched_fields'].append('SURNAME')

            # check date of birthday (DOB)
            dob_fields = []
            for dob_field in ['DayOfBirth', 'MonthOfBirth', 'YearOfBirth']:
                dob_field_check = next(
                    (field for field in datasource['DatasourceFields'] if field["FieldName"] == dob_field), None)
                if dob_field_check:
                    dob_fields.append(dob_field_check)

            # If all the fields belonging to dob found in the datasource fields are matches
            if dob_fields and all(field["Status"] == "match" for field in dob_fields):
                match['matched_fields'].append('DOB')

            address_fields = []
            for address_field in ['BuildingNumber',
                                  'BuildingName',
                                  'UnitNumber',
                                  'StreetName',
                                  'City',
                                  'Suburb',
                                  'County',
                                  'StateProvinceCode',
                                  'PostalCode']:
                address_field_check = next(
                    (field for field in datasource['DatasourceFields'] if field["FieldName"] == address_field), None)
                if address_field_check:
                    address_fields.append(address_field_check)
            # If all the fiels belonging to address found in the datasource filds are with match status
            address_sent = trulioo_request.get('Location', {})
            fields_sent = set((
                field for field, value in address_sent.items()
                if value
            ))

            address_matches = {
                field['FieldName']: field['Status']
                for field in address_fields
            }

            if is_full_address(fields_sent) and all((
                address_matches.get(field_sent) == 'match' for field_sent in fields_sent
            )):
                match['matched_fields'].append('ADDRESS')

            # check national id
            national_id_field = next((field for field in datasource['DatasourceFields'] if field['FieldName'].lower() in [
                'nationalid',
                'health',
                'socialservice',
                'taxidnumber',
            ]), None)
            if national_id_field and national_id_field['Status'] == 'match':
                match['matched_fields'].append('IDENTITY_NUMBER')

            # if have matches add
            if match['matched_fields']:
                match['count'] = 1

            matches.append(match)

    if matches:
        response_body['output_data']["entity_type"] = "INDIVIDUAL"
        response_body['output_data']["electronic_id_check"] = {
            "matches": matches}

    transaction_id = trulioo_data.get('TransactionID')
    if transaction_id:
        response_body['output_data'].setdefault('electronic_id_check', {})['provider_reference_number'] = transaction_id

    return response_body


def make_error(*, code, message, info={}):
    return {
        'code': code,
        'message': message,
        'info': {
            'provider': 'Trulioo',
            'timestamp': str(datetime.now()),
            **info,
        },
    }


missing_field_mapping = {
    'DayOfBirth': '/personal_details/dob',
    'MonthOfBirth': '/personal_details/dob',
    'YearOfBirth': '/personal_details/dob',
    'FirstGivenName': '/personal_details/name/given_names/0',
    'MiddleName': '/personal_details/name/given_names/1',
    'FirstSurName': '/personal_details/name/family_name',
    'BuildingNumber': '/address_history/0/street_number',
    'BuildingName': '/address_history/0/premise',
    'UnitNumber': '/address_history/0/subpremise',
    'StreetName': '/address_history/0/route',
    'PostalCode': '/address_history/0/postal_code',
    'Suburb': '/address_history/0/postal_town',
    'City': '/address_history/0/locality',
    'StateProvinceCode': '/address_history/0/state_province',
    'EmailAddress': '/contact_details/email',
    'Telephone': '/contact_details/phone_number',
    'IPAddress': '/ip_location',
}


def extract_passfort_missing_field(trulioo_error):
    message = trulioo_error.get('Message')
    if message:
        components = message.split('Missing required field: ')
        if len(components) == 2:
            return missing_field_mapping.get(components[1])

    return None


def interpret_missing_field_errors(trulioo_errors):
    info = {'original_error': trulioo_errors}
    missing_fields = [
        missing_field for missing_field in {
            extract_passfort_missing_field(trulioo_error)
            for trulioo_error in trulioo_errors
        }
        if missing_field is not None
    ]

    if missing_fields:
        info['missing_fields'] = missing_fields

    return make_error(
        code=101,
        message='Missing required fields',
        info=info,
    )


def trulioo_to_passfort_errors(trulioo_errors):
    errors = []
    missing_field_errors = []
    for trulioo_error in trulioo_errors:
        error_code = trulioo_error.get('Code')
        if error_code in ('1001', '4001', '3005'):
            missing_field_errors.append(trulioo_error)
        elif error_code in ('1006', '1008'):
            errors.append(make_error(
                code=201,
                message=f'The submitted data was invalid. Provider returned error code {error_code}',
                info={
                    'original_error': trulioo_error,
                },
            ))
        else:
            message = trulioo_error.get('Message', 'Unknown error')
            errors.append(make_error(
                code=303,
                message=f"Provider Error: {message} while running 'Trulioo' service",
                info={
                    'original_error': trulioo_error,
                },
            ))

    if missing_field_errors:
        errors.append(interpret_missing_field_errors(missing_field_errors))

    return errors
