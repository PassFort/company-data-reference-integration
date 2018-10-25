import json


def get_response_from_file(search_ref, folder='mock_data'):
    with open(f'{folder}/{search_ref}.json', 'rb') as f:
        return json.loads(f.read())

