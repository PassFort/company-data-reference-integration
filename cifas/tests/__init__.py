from os import path
from json import loads


def read_test_data(name: str) -> str:
    with open(path.join(path.dirname(__file__), name)) as file:
        return file.read()


MEMBERS_RESPONSE = read_test_data('members.xml')
MATCH_RESPONSE = read_test_data('match.xml')
NOMATCH_RESPONSE = read_test_data('nomatch.xml')
INDIVIDUAL_DATA_FULL = loads(read_test_data('individual_data_full.json'))
INDIVIDUAL_DATA_MINIMAL = loads(read_test_data('individual_data_minimal.json'))
COMPANY_DATA_FULL = loads(read_test_data('company_data_full.json'))
COMPANY_DATA_MINIMAL = loads(read_test_data('company_data_minimal.json'))
