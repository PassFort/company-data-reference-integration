from os import path
from json import loads


def read_test_data(name: str) -> str:
    with open(path.join(path.dirname(__file__), name)) as file:
        return file.read()


MATCH_RESPONSE = read_test_data('match.xml')
NOMATCH_RESPONSE = read_test_data('nomatch.xml')
INDIVIDUAL_DATA_FULL = loads(read_test_data('individual_data_full.json'))
INDIVIDUAL_DATA_MINIMAL = loads(read_test_data('individual_data_minimal.json'))
