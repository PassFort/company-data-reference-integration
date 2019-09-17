import json
from app.UKCharitiesCommission import UKCharitiesCommission

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
    charities_commission = UKCharitiesCommission(CREDENTIALS)
    raw_data, formatted_data = charities_commission.get_charity(charity_name)

    with open(f'test_data/RAW_{i}.xml', 'wb') as f:
        f.write(raw_data)

    with open(f'test_data/FORMATTED_{i}.json', 'w') as f:
        f.write(json.dumps(formatted_data, indent=4))

if __name__ == '__main__':
    for i, charity_name in enumerate(charities):
        save_data(charity_name, i)
