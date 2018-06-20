from pipetools import pipe
import re
import logging
from functools import partial
from typing import List

def stage_error_from_onfido_response(response, connection_error_message):
    if isinstance(response, dict):
        errors = response.get('error')
        return {
            "error": errors,
        }
    else:
        return {
            "error": connection_error_message,
        }


first_cap_re = re.compile('(.)([A-Z][a-z]+)')
all_cap_re = re.compile('([a-z0-9])([A-Z])')


def to_snake_case(name: str) -> str:
    name_no_space = name.replace(" ", "")
    s1 = first_cap_re.sub(r'\1_\2', name_no_space)
    return all_cap_re.sub(r'\1_\2', s1).lower()


onfido_to_passfort_matches = {
    'credit_agencies':  '',
    'voting_register': 'electoral_',
    'telephone_database': 'telephone_',
    'government': 'government_',
    'business_registration': 'business_registration_',
    'consumer_database': 'consumer_',
    'utility_registration': 'utility_',
    'postal_authorities': 'postal_',
    'commercial_database': 'commercial_',
    'proprietary': 'onfido_proprietary_',
    'ssn': 'ssn_',
    # 'Register of death': '',
}

def set_appends_in_dict(appenders: List[str], a_dict, base_key: str, value):
    for appender in appenders:
        a_dict[base_key + appender] = value

set_address_in_dict = partial(set_appends_in_dict, ['exact', 'partial'])
set_dob_in_dict = partial(set_appends_in_dict, ['dob'])
def source_counts_to_individual(source_breakdown):
    address = source_breakdown['address']
    dob = source_breakdown['dob']
    database_matches_init = {}
    credit_ref_matches_init = {}

    def source_count_to_match(is_address, source_name, source_match_count):
        set_in_dict = set_address_in_dict if is_address else set_dob_in_dict
        count = int(source_match_count['count'])
        match_count = ({'v': {'count': count, 'match': count > 0}})
        if source_name == 'credit_agencies':
            set_in_dict(credit_ref_matches_init, onfido_to_passfort_matches[source], match_count)
        else:
            set_in_dict(database_matches_init, onfido_to_passfort_matches[source], match_count)

    for source, source_count in address.items():
        source_count_to_match(True, source, source_count)

    for source, source_count in dob.items():
        source_count_to_match(False, source, source_count)

    if source_breakdown['is_alive'] == False:
        database_matches_init['mortality_list'] = ({'v': {'count': 1, 'match': True}})
    return ({
        'db_matches': database_matches_init,
        'credit_ref': credit_ref_matches_init,
    })


# TODO: The docs say one thing, and the actual response says another. Ask onfido if docs wrong or if we should
# handle both.
def get_number_of_agencies(properties):
    possible1 = properties.get('number_of_agencies')
    possible2 = properties.get('number_of_credit_agencies')

    return possible1 or possible2 or 1


def parsed_onfido_breakdown(breakdown):
    source_match_count = {
        'credit_agencies': {'count': 0},
        'voting_register': {'count': 0},
        'telephone_database': {'count': 0},
        'government': {'count': 0},
        'business_registration': {'count': 0},
        'consumer_database': {'count': 0},
        'utility_registration': {'count': 0},
        'postal_authorities': {'count': 0},
        'commercial_database': {'count': 0},
        'proprietary': {'count': 0},
    }
    source_results = breakdown['breakdown']
    for source, source_result in source_results.items():

        # For USA and other countries, the structure of onfido data differs!
        if source == 'address_matched' or source == 'date_of_birth_matched':
            if source_result['result'] is not 'clear':
                continue
            sources = map(to_snake_case, source_result['properties']['sources'].split(','))
            for actual_source in sources:
                if actual_source in source_match_count:
                    source_match_count[actual_source] = {'count': 1}
                else:
                    logging.info('Did not handle source %s', actual_source)
            return source_match_count
        elif source == 'credit_agencies':  # Handle special case where count reported is explicit number
            count = get_number_of_agencies(source_result['properties']) if source_result['result'] == 'clear' else 0
        else:
            count = 1 if source_result['result'] == 'clear' else 0

        if source in source_match_count:
            source_match_count[source]['count'] = count
        else:
            logging.info('Did not handle source %s', source)
    return source_match_count


def onfido_to_source_counts(response):
    breakdowns = response.get('breakdown')
    address_and_name_match = {}
    dob_and_name_match = {}
    ssn_match = {}
    mortality = None
    for result_type, breakdown in breakdowns.items():
        if result_type == 'address':
            address_and_name_match = parsed_onfido_breakdown(breakdown)
        if result_type == 'date_of_birth':
            dob_and_name_match = parsed_onfido_breakdown(breakdown)
        if result_type == 'mortality':
            mortality = breakdown['result'] == 'clear'
        if result_type == 'ssn':
            ssn_match = {'ssn': {'count': 1 if breakdown['result'] == 'clear' else 0}}
    return {'address': {**ssn_match, **address_and_name_match}, 'dob': dob_and_name_match, 'is_alive': mortality}


def get_report_from_check(check):
    return [report for report in check['reports'] if report['name'] == 'identity'][0]


onfido_check_to_individual = pipe | get_report_from_check | onfido_to_source_counts | source_counts_to_individual
