import json


def get_response_from_file(file_name, folder='demo_data'):
    with open(f'{folder}/{file_name}.json', 'rb') as f:
        return json.loads(f.read())

