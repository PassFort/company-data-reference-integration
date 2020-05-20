import pycountry
import json
from datetime import datetime

def passfort_to_worldview_data(passfort_data):
    worldview_pkg = {}

    input_data = passfort_data.get('input_data')

    if input_data:
        # check personal details
        personal_details = input_data.get('personal_details')

        if personal_details:
            identity = {}

            # check name details
            name_details = personal_details.get('name')

            if name_details:
                given_names = name_details.get('given_names')

                if given_names:
                    identity['givenfullname'] = given_names[0]
                
                family_name = name_details.get('family_name')

                if family_name:
                    identity['surnameFirst'] = family_name
                
                if given_names and family_name:
                    # Let me know if you find this too convoluted.
                    # I tried to make it small and safe for joining 
                    # a string list with a single string in one line.
                    identity['completename'] = ' '.join([*given_names, family_name])
            
            # check date of birth
            dob = personal_details.get('dob')

            if dob:
                if len(dob) <= 4:
                    date_of_birth = dob
                elif len(dob) <= 7 and '-' in dob:
                    date_of_birth = datetime.strptime(dob, '%Y-%M').strftime('%M/%Y')
                else:
                    date_of_birth = datetime.strptime(dob, '%Y-%M-%d').strftime('%M/%d/%Y')
                
                identity['dob'] = date_of_birth
            
            # check personal number
            national_identity_number = personal_details.get('national_identity_number')

            if national_identity_number:
                # national_identity_number is a dict/object 
                # with country as the key and the number as value. 
                # We just need to get the first value.
                identity['nationalid'] = list(national_identity_number.values())[0]
            
            # check gender
            gender = personal_details.get('gender')

            if gender:
                identity['gender'] = gender
            
            worldview_pkg['identity'] = identity
            
        # check address details
        address_history = input_data.get('address_history')

        if address_history:
            # GDC allows only one address per search.
            # We need to get the last history entry.
            address_details = address_history[-1].get('address')

            if address_details:
                address = {}
                
                address_parts = []


                street_number = address_details.get('street_number')
                route = address_details.get('route')
                premise = address_details.get('premise')

                if street_number:
                    address_parts.append(street_number)
                
                if route:
                    address_parts.append(route)

                if premise:
                    address_parts.append(premise)

                address_line_1 = ' '.join(address_parts)

                if address_line_1:
                    address['addressLine1'] = address_line_1

                houseNumber = address_details.get('subpremise')

                if houseNumber:
                    address['houseNumber'] = houseNumber

                locality = address_details.get('locality')

                if locality:
                    address['locality'] = locality
                
                postal_code = address_details.get('postal_code')

                if postal_code:
                    address['postalCode'] = postal_code
                
                postal_town = address_details.get('postal_town')

                if postal_town:
                    address['district'] = postal_town
                
                state_province = address_details.get('state_province')

                if state_province:
                    address['province'] = state_province
                
                countryCode = address_details.get('country')

                if countryCode:
                    # GDC uses only 2 alpha country code and PassFort uses 3. (e.g: GBR -> GB)
                    country = pycountry.countries.get(alpha_3=countryCode)
                    address['countryCode'] = country.alpha_2

                worldview_pkg['address'] = address
        
        contact_details = input_data.get('contact_details')

        if contact_details:
            email = contact_details.get('email')
            phone_number = contact_details.get('phone_number')

            if email:
                worldview_pkg['email'] = { 'fullEmailAddress': email }

            if phone_number:
                worldview_pkg['phone'] = { 'phoneNumber': phone_number }
    
    return worldview_pkg

NOT_FOUND = -1
SEPARATOR_COUNT = 3
PARTS_COUNT = 4
RELIABLE = '10' # this is the code for reliable messages
FULL_MATCH = '1' # this is the code for full matches
PASS = 'PASS'
ERROR = 'ERROR'
DATABASES = {
    "CRD": "Credit",
    "GVT": "Government",
    "CMM": "Commercial",
    "CNS": "Consumer",
    "OTH": "Other (including social)",
    "UTL": "Utility",
    "PRP": "Proprietary",
    "TEL": "Telco",
    "PST": "Postal",
}

FIELDS_TO_MATCH = {
    'FIRSTNAME': 'FORENAME',
    'LASTNAME': 'SURNAME',
    'DATEOFBIRTH': 'DOB',
    'ADDRESS': 'ADDRESS',
}

class MatchResult():
    def __init__(self, source):
        super().__init__()

        split_list = source.split('-')

        if not len(split_list) == PARTS_COUNT:
            raise Exception(f'Code must have {PARTS_COUNT} parts')

        match_code, country_code, database_code, field_name = split_list

        self.full_match = match_code[0] == FULL_MATCH

        self.source = source
        self.match_code = match_code
        self.country_code = country_code

        # all returned database codes comes with a trailing number 
        # we won't need. E.g: CMM1 -> CMM (Commercial)
        self.database_code = database_code[:-1]
        self.database_name = DATABASES[self.database_code]
        self.database_type = 'CREDIT' if self.database_code == 'CRD' else 'CIVIL'

        self.field_name = field_name
        
# we defined some lambda functions to make the code more readable and also to stick do DRY principles
is_valid_message = lambda message: bool(message.get('code')) and message['code'].count('-') == SEPARATOR_COUNT and message['code'].find('MATCHED') == NOT_FOUND
is_valid_field = lambda field: field in FIELDS_TO_MATCH.keys()
is_full_match = lambda code: code.full_match == True # we only care about full matches
is_section_reliable = lambda section: section['codes']['reliability'] == RELIABLE
map_codes = lambda section: [ MatchResult(message['code']) for message in section['codes']['messages'] if is_valid_message(message) ]

def worldview_to_passfort_data(worldview_response_data):
    status = worldview_response_data.get('status')
    body = worldview_response_data.get('body')

    # base response
    response_body = {
        "output_data": {
            "decision": 'FAIL',
            "entity_type": "INDIVIDUAL",
            "electronic_id_check": {"matches": []}
        },
        "raw": body,
        "errors": []
    }

    if status >= 400:
        # we were not able to find any GDC docs regarding error handling and 
        # based on our tests they also do not provide them through HTTP response codes
        # except for those listed below.
        if status in [401, 403]:
            response_body['errors'].append({
                'code': 302,
                'message': 'Provider Error: Required credentials are missing for the request.'
            })
        else:
            response_body['errors'].append({
                'code': 303,
                'message': f'Provider Error: UNKNOWN ERROR: {body}'
            })
        
        response_body['output_data']['decision'] = ERROR

    if status == 200:
        address = body.get('address')
        address_codes = []

        # we only care about reliable messages
        if address and is_section_reliable(address):
            address_codes = map_codes(address)

        identity = body.get('identity')
        identity_codes = []

        if identity and is_section_reliable(identity):
            identity_codes = map_codes(identity)

        # we have multiple sources to deal but they will be 
        # handled the same way so we join all codes together
        all_codes = [*address_codes, *identity_codes]

        matches = []
        print(all_codes)
        for code in [code for code in all_codes if is_full_match(code) and is_valid_field(code.field_name)]:
            print(code)
            filtered = list(filter(lambda entry: entry['database_name'] == code.database_name, matches))

            if filtered:
                match = filtered[0]
            else:
                match = {
                    "database_name": code.database_name,
                    "database_type": code.database_type,
                    "matched_fields": [],
                    "count": 0,
                }

                matches.append(match)
            
            match['matched_fields'].append(FIELDS_TO_MATCH[code.field_name])
            match['count'] += 1

        response_body['output_data']['electronic_id_check']['matches'] = matches

        if matches:
            response_body['output_data']['decision'] = PASS

    return response_body
