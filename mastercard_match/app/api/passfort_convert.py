import logging
import hashlib
import random
import uuid
from fuzzywuzzy import fuzz

from app.api.match import termination_reason_mapping, termination_reason_description_mapping


def address_to_passfort_format(address):
    if not address:
        return None
    address_lines = []
    line1 = address.get('Line1')
    line2 = address.get('Line2')
    if line1:
        address_lines.append(line1)
    if line2:
        address_lines.append(line2)

    return {
        'country': address.get('Country'),
        'locality': address.get('City'),
        'state_province': address.get('CountrySubdivision'),
        'postal_code': address.get('PostalCode'),
        'address_lines': address_lines,
    }


def driving_licence_to_passfort_format(driving_licence):
    if not driving_licence:
        return None
    return {
        'document_type': 'DRIVING_LICENCE',
        'number': driving_licence.get('Number', 'Unknown'),
        'country_code': driving_licence.get('Country', '000'),
        'issuing_state': driving_licence.get('CountrySubDivision'),
    }


def contact_details_to_passfort(contact_details):
    def build_name_value(name, data):
        return {'name': name, 'value': data.get(name)}
    fields = ['bank_name', 'first_name', 'last_name', 'phone_number', 'fax_number', 'email_address']
    return [{
        'source_name': cdata.get('bank_name'),
        'other_details': [build_name_value(name, cdata) for name in fields]
    } for cdata in contact_details]


def match_from_in_out(match_type, input_value, output_value):
    if not match_type:
        return None
    severity = {
        'M00': 'No match',
        'M01': 'Exact match',
        'M02': 'Phonetic match',
    }
    match_severity = severity.get(match_type, 'Unknown')
    if match_severity == 'Unknown':
        logging.error(f'Unknown match_type {match_type}')

    return {
        'provider_match_type': match_type,
        'match_strength_description': match_severity,
        'inquiry_data': input_value,
        'match_data': output_value,
    }


def find_exact_matching_associate(input_principals, matches, output_principal):
    for (idx, principal) in enumerate(input_principals):
        for (matched_field, match_type) in matches:
            found = check_field(principal, output_principal, matched_field)
            if found:
                return idx


def find_fuzzy_matching_associate(input_principals, matches, output_principal):
    num_matches = len(matches)
    scores = []
    for (idx, principal) in enumerate(input_principals):
        score = 0
        for (matched_field, match_type) in matches:
            score += check_field(principal, output_principal, matched_field, fuzzy=True)
        scores.append((score / num_matches, idx))

    return sorted(scores, key=lambda x: x[0], reverse=True)[0][1]


def check_field(input_principal, output_principal, field_name, fuzzy=False):
    if field_name in check_for_field:
        return check_for_field.get(field_name)(input_principal, output_principal, fuzzy=fuzzy)
    else:
        input_value = input_principal.get(field_name).lower()
        output_value = output_principal.get(field_name).lower()
        if fuzzy:
            return fuzz.ratio(input_value, output_value)
        else:
            return input_value == output_value


def check_inner_field(inp, out, field, fuzzy=False):
    inp_data = inp.get(field, '').lower()
    out_data = out.get(field, '').lower()
    if fuzzy:
        return fuzz.ratio(inp, out)
    if not inp_data or not out_data:
        return True
    return inp_data == out_data


def check_name(input_principal, output_principal, fuzzy=False):
    input_value = join_names(input_principal).lower()
    output_value = join_names(output_principal).lower()
    if fuzzy:
        return fuzz.ratio(input_value, output_value)
    return input_value == output_value


def check_address(input_principal, output_principal, fuzzy=False):
    fields = ['Country', 'City', 'Line1', 'CountrySubdivision', 'PostalCode']
    input_data = input_principal.get('Address')
    output_data = output_principal.get('Address')
    if fuzzy:
        return sum(check_inner_field(input_data, output_data, f, True) for f in fields) / len(fields)
    return all(check_inner_field(input_data, output_data, f) for f in fields)


def check_driving_license(input_principal, output_principal, fuzzy=False):
    fields = ['Number', 'Country', 'CountrySubDivision']
    input_data = input_principal.get('DriversLicense')
    output_data = output_principal.get('DriversLicense')
    if fuzzy:
        return sum(check_inner_field(input_data, output_data, f, True) for f in fields) / len(fields)
    return all(check_inner_field(input_data, output_data, f) for f in fields)


check_for_field = {
    'Name': check_name,
    'Address': check_address,
    'DriversLicense': check_driving_license
}


def join_names(principal):
    if not principal:
        return None
    return principal['FirstName'] + ' ' + principal['LastName']


def build_associate_matches(output_data, input_data, match_data, associate_id):
    def build_simple_match(field_name):
        if not match_data.get(field_name):
            return None
        return match_from_in_out(match_data[field_name], input_data.get(field_name), output_data.get(field_name))

    return {
        'name': match_from_in_out(match_data.get('Name'), join_names(input_data), join_names(output_data)),
        'phone_number': build_simple_match('PhoneNumber'),
        'alt_phone_number': build_simple_match('AltPhoneNumber'),
        'national_id': build_simple_match('NationalId'),
        'address': match_from_in_out(
            match_data.get('Address'),
            address_to_passfort_format(input_data.get('Address')),
            address_to_passfort_format(output_data.get('Address')),
        ),
        'driving_licence': match_from_in_out(
            match_data.get('DriversLicense'),
            driving_licence_to_passfort_format(input_data.get('DriversLicense')),
            driving_licence_to_passfort_format(output_data.get('DriversLicense')),
        ),
        'associate_id': associate_id,
    }


def build_company_matches(output_data, input_data, match_data):
    def build_simple_match(field_name):
        if not match_data.get(field_name):
            return None
        return match_from_in_out(match_data[field_name], input_data.get(field_name), output_data.get(field_name))
    return {
        'name': build_simple_match('Name'),
        'doing_business_as_name': build_simple_match('DoingBusinessAsName'),
        'phone_number': build_simple_match('PhoneNumber'),
        'address': match_from_in_out(
            match_data.get('Address'),
            address_to_passfort_format(input_data.get('Address')),
            address_to_passfort_format(output_data.get('Address')),
        ),
        'national_tax_id': build_simple_match('NationalTaxId'),
        'country_sub_division_tax_id': build_simple_match('CountrySubDivisionTaxId')
    }


def generate_match_id(output_merchant):
    match_id = str(uuid.uuid4())
    date = output_merchant.get('AddedOnDate')
    added_by = output_merchant.get('AddedByAcquirerID')
    if date and added_by:
        match_id = date + added_by
    return match_id


def merchant_to_event(output_merchant, input_merchant, associate_ids):
    output_data = output_merchant.to_primitive()
    input_data = input_merchant.to_primitive()
    matched_fields = output_data['MerchantMatch']
    principals_matched_fields = matched_fields['PrincipalMatch']
    input_principals = input_data['Principal']
    output_principals = output_data['Principal']

    company_matches = build_company_matches(output_data, input_data, matched_fields)
    match_reason_code = output_data.get('TerminationReasonCode')

    event = {
        'event_type': 'FRAUD_FLAG',
        'company_match_fields': company_matches,
        'match_id': generate_match_id(output_data),
    }
    if match_reason_code:
        match_reason_title = termination_reason_mapping.get(match_reason_code, 'Unknown')
        if match_reason_title == 'Unknown':
            logging.error(f'Unknown match reason code {match_reason_code}')

        match_reason_description = termination_reason_description_mapping.get(match_reason_code)
        event['match_reason_code'] = match_reason_code + ' - ' + match_reason_title
        event['match_reason_description'] = match_reason_description
        event['entry_date'] = output_data.get('AddedOnDate')

        contact_details = output_merchant.get('contact_details')
        if contact_details:
            event['source_contact_details'] = contact_details_to_passfort(contact_details)

    associate_match_fields = []
    for (idx, p_matched_fields) in enumerate(principals_matched_fields):
        output_principal = output_principals[idx]

        found_index = None
        associate_id = None
        exact_fields = [(k, v) for (k, v) in p_matched_fields.items() if v == 'M01']
        phonetic_fields = [(k, v) for (k, v) in p_matched_fields.items() if v == 'M02']

        input_principal = {}

        if exact_fields or phonetic_fields:
            # Skip matching if we have only 1 input associate
            if len(input_principals) == 1:
                found_index = 0
            else:
                # Try matching on exact fields if we fail try to fuzzy match
                if exact_fields:
                    found_index = find_exact_matching_associate(input_principals, exact_fields, output_principal)
                if not found_index and phonetic_fields:
                    found_index = find_fuzzy_matching_associate(input_principals, phonetic_fields, output_principal)
            if found_index is not None:
                input_principal = input_principals[found_index]
                associate_id = associate_ids[found_index]

        associate_match_fields.append(build_associate_matches(
            output_principal, input_principal, p_matched_fields, associate_id
        ))
    event['associate_match_fields'] = associate_match_fields
    return event
