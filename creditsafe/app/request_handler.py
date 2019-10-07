import requests

import pycountry
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry

from .api.types import CreditSafeAuthenticationError, CreditSafeSearchError, CreditSafeReportError, \
    SearchInput
from .api.internal_types import CreditSafeCompanySearchResponse, CreditSafeCompanyReport


def requests_retry_session(
        retries=3,
        backoff_factor=0.3,
        session=None,
):
    session = session or requests.Session()
    retry = Retry(
        total=retries,
        read=retries,
        connect=retries,
        backoff_factor=backoff_factor
    )
    adapter = HTTPAdapter(max_retries=retry)
    session.mount('https://', adapter)
    session.timeout = 10
    return session


class CreditSafeHandler:

    def __init__(self, credentials):
        self.base_url = 'https://connect.creditsafe.com/v1'
        self.credentials = credentials
        self.session = requests_retry_session()

    def get_token(self, username, password):
        response = self.session.post(
            f'{self.base_url}/authenticate',
            json={
                'username': username,
                'password': password
            }
        )

        if response.status_code != 200:
            raise CreditSafeAuthenticationError(response)

        return response.json()['token']

    def search(self, input_data: SearchInput, fuzz_factor):
        # Valid for 1 hour. Multiple valid tokens can exist at the same time.
        token = self.get_token(self.credentials.username, self.credentials.password)

        queries = input_data.build_queries()

        companies = []
        raw = []
        found_ids = set()

        for query in queries:
            url = f'{self.base_url}/companies?{query}&pageSize=100'
            response = self.session.get(
                url,
                headers={
                    'Content-Type': 'application/json',
                    'Authorization': f'Bearer {token}'
                })

            if response.status_code != 200 and len(companies) == 0:
                # Only raise the error if we didn't find any companies so far
                # E.g:
                # the name search returned results, but the regNo search errored, then
                # we are safe to ignore the error
                raise CreditSafeSearchError(response)

            result = response.json()
            raw.append(result)

            for r in result.get('companies', []):
                c = CreditSafeCompanySearchResponse.from_json(r)
                if c.registration_number is None:
                    continue
                if c.creditsafe_id in found_ids:
                    continue
                found_ids.add(c.creditsafe_id)
                if not c.matches_search(input_data, fuzz_factor=fuzz_factor):
                    continue
                companies.append(c)

            if len(companies) >= 20:
                break

        print([c.serialize() for c in companies])

        companies = sorted(
            companies,
            key=lambda co: co.name_match_confidence(input_data),
            reverse=True
        )
        print([c.serialize() for c in companies])
        formatted_companies = [
            c.as_passfort_format(
                input_data.country, input_data.state)
            for c in companies
        ][0:20]  # Only get the first 20
        return raw, formatted_companies

    def exact_search(self, name, country, state=None):
        try:
            raw, companies = self.search(
                SearchInput({'name': name, 'country': country, 'state': state}),
                fuzz_factor=95
            )

            if len(companies) == 1:
                return companies[0]
            else:
                for company in companies:
                    if company['name'] == name:
                        return company
        except Exception:
            pass

        return None

    def get_report(self, input_data):
        # Valid for 1 hour. Multiple valid tokens can exist at the same time.
        token = self.get_token(self.credentials.username, self.credentials.password)
        url = f'{self.base_url}/companies/{input_data.creditsafe_id}'
        if input_data.country_of_incorporation == 'DEU':
            url = f'{url}?customData=de_reason_code::1'  # 1 is code for Credit Decisioning
        response = self.session.get(
            url,
            headers={
                'Content-Type': 'application/json',
                'Authorization': f'Bearer {token}'
            }
        )

        if response.status_code != 200:
            raise CreditSafeReportError(response)

        raw = response.json()
        return raw, CreditSafeCompanyReport.from_json(raw['report']).as_passfort_format(self)
