from app.utils import base_request, post

country_map = {
    'AL': 'ALB',
    'BE': 'BEL',
    'BS': 'BHS',
    'BM': 'BMU',
    'CH': 'CHE',
    'CY': 'CYP',
    'DE': 'DEU',
    'DK': 'DNK',
    'FI': 'FIN',
    'FR': 'FRA',
    'GB': 'GBR',
    'GG': 'GGY',
    'GL': 'GRL',
    'HK': 'HKG',
    'IM': 'IMN',
    'IE': 'IRL',
    'IS': 'ISL',
    'IL': 'ISR',
    'JE': 'JEY',
    'LI': 'LIE',
    'LU': 'LUX',
    'LV': 'LVA',
    'MT': 'MLT',
    'ME': 'MNE',
    'NL': 'NLD',
    'NO': 'NOR',
    'PL': 'POL',
    'RO': 'ROU',
    'SK': 'SVK',
    'SL': 'SVN',
    'SE': 'SWE',
}


def request_company_search(country_code, search_term, credentials, offset=0, limit=20):
    def format_company(company):
        return {
            'name': company['name'],
            'number': company['companyId'],
            'country': country_map[company['countryCode']],
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
