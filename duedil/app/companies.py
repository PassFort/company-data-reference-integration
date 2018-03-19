from app.utils import base_request, post
from app.utils import convert_country_code


def request_company_search(country_code, search_term, credentials, offset=0, limit=20):
    def format_company(company):
        return {
            'name': company['name'],
            'number': company['companyId'],
            'country': convert_country_code(company['countryCode']),
        }

    url = f'/search/companies.json?offset={offset}&limit={limit}'
    data = {
        'criteria': {
            'name': search_term,
            'countryCodes': {
                'values': [country_code],
                'mode': 'any'
            }
        }
    }
    _, json = base_request(url, credentials, post, data)

    return json, [format_company(company) for company in json['companies']]
