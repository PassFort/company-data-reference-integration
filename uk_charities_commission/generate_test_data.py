import json
from app.charities import get_charity

CREDENTIALS = {
    "api_key": "60b5b1c4-3a08-4cc2-b"
}

charities = [
    'MacMillan Cancer Support',
    'Air Ambulance Service',
    'Cancer Research UK',
    'Meath Epilepsy Charity',
    'Middlesbrough Diocesan Trust',
    'The Hamlet Centre Trust',
    'Children with Cancer UK',
]

def save_data(charity_name, i):
    raw_data, formatted_data = get_charity(charity_name, CREDENTIALS)

    with open(f'test_data/RAW_{i}.json', 'w') as f:
        f.write(json.dumps(raw_data, indent=4))

    with open(f'test_data/FORMATTED_{i}.json', 'w') as f:
        f.write(json.dumps(formatted_data, indent=4))

if __name__ == '__main__':
    for i, charity_name in enumerate(charities):
        save_data(charity_name, i)
