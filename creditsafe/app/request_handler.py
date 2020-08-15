from datetime import datetime, timedelta
from itertools import chain, groupby

import logging
import requests

from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry

from .api.types import CreditSafeAuthenticationError, CreditSafeSearchError, CreditSafeReportError, \
    SearchInput, CreditSafeMonitoringError, CreditSafeMonitoringRequest, CreditSafeMonitoringEventsRequest
from .api.internal_types import CreditSafeCompanySearchResponse, CreditSafeCompanyReport, \
    CreditSafePortfolio, CreditSafeNotificationEventsResponse, CreditSafeNotificationEvent, EventsConfigGroup
from .api.event_mappings import get_configure_event_payload


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

        companies = sorted(
            companies,
            key=lambda co: co.name_match_confidence(input_data),
            reverse=True
        )
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

    def get_report_41(self, input_data):
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
        if raw.get['report'] is None:
            logging.error(f'Report not found: {raw}')
            raise CreditSafeReportError(response)

        return raw, CreditSafeCompanyReport.from_json(raw['report']).as_passfort_format_41(self)

    def create_portfolio(self, name):
        # Valid for 1 hour. Multiple valid tokens can exist at the same time.
        token = self.get_token(self.credentials.username, self.credentials.password)
        url = f'{self.base_url}/monitoring/portfolios'

        response = self.session.post(
            url,
            json={
                'name': name,
                'isDefault': False
            },
            headers={
                'Content-Type': 'application/json',
                'Authorization': f'Bearer {token}'
            }
        )

        if response.status_code != 200:
            raise CreditSafeMonitoringError(response)

        portfolio = CreditSafePortfolio.from_json(response.json())
        self._configure_events(token, portfolio.id)
        return portfolio

    def monitor_company(self, monitor_company: CreditSafeMonitoringRequest):
        # Valid for 1 hour. Multiple valid tokens can exist at the same time.
        token = self.get_token(self.credentials.username, self.credentials.password)
        portfolio_company_url = f'{self.base_url}/monitoring/portfolios/{monitor_company.portfolio_id}/companies'

        company_response = self.session.get(
            f'{portfolio_company_url}/{monitor_company.creditsafe_id}',
            headers={
                'Content-Type': 'application/json',
                'Authorization': f'Bearer {token}'
            }
        )

        # if company doesn't already exist in the portfolio, add it
        if company_response.status_code == 404 or (company_response.status_code == 400 \
                and company_response.json()['message'] == 'PortfolioCompany not found'):
            response = self.session.post(
                portfolio_company_url,
                json={
                    'id': monitor_company.creditsafe_id,
                    'personalReference': '',
                    'freeText': '',
                    'personalLimit': '' # todo ask creditsafe what this should be
                },
                headers={
                    'Content-Type': 'application/json',
                    'Authorization': f'Bearer {token}'
                }
            )

            if response.status_code != 201 and response.status_code != 200:
                raise CreditSafeMonitoringError(response)
        elif company_response.status_code != 200:
            raise CreditSafeMonitoringError(company_response)

    def handle_events(self, request_data: CreditSafeMonitoringEventsRequest):
        last_run_dates = {config.last_run_date for config in request_data.monitoring_configs}

        # Creditsafe updates events in batches, daily.
        # Look for events only until the previous day in case they haven't been populated yet
        end_date = datetime.now() - timedelta(days=1)
        if any(start_date >= end_date for start_date in last_run_dates):
            return

        # Valid for 1 hour. Multiple valid tokens can exist at the same time.
        token = self.get_token(self.credentials.username, self.credentials.password)
        url = f'{self.base_url}/monitoring/notificationEvents'

        event_groups = []

        # For each unique last_run_date in the config list, call the creditsafe endpoint to get
        # the all the events in that time period, and group the events by portfolio ID.
        for start_date in last_run_dates:
            raw_events = self._get_events_by_last_run_date(token, url, start_date, end_date)

            sorted_events = sorted(raw_events, key=lambda e: e.company.portfolio_id)
            for portfolio_id, events_iter in groupby(sorted_events, key=lambda e: e.company.portfolio_id):
                raw_events = []
                for event in events_iter:
                    raw_events.append(event)

                event_groups.append(EventsConfigGroup(start_date, portfolio_id, raw_events))

        for config in request_data.monitoring_configs:
            # Get the group of events with the same portfolio ID and last_run_date as the config
            group = next(
                (g for g in event_groups if g.last_run_date == config.last_run_date and g.portfolio_id == config.portfolio_id),
                None
            )

            passfort_events = self._get_passfort_events(group.raw_events) if group else []
            raw_events = [e.to_primitive() for e in group.raw_events] if group else []

            self._send_monitoring_callback(request_data.callback_url, config, passfort_events, raw_events, end_date)

    def _get_passfort_events(self, raw_events):
        events = [e.to_passfort_format() for e in raw_events]
        return [e.to_primitive() for e in events if e]

    def _send_monitoring_callback(self, callback_url, config, passfort_events, raw_events, end_date):
        response = requests.post(
            callback_url,
            json={
                'institution_config_id': str(config.institution_config_id),
                'portfolio_id': config.portfolio_id,
                'last_run_date': end_date.isoformat(),
                'events': passfort_events,
                'raw_data': raw_events
            })
        response.raise_for_status()

    def _get_events_by_last_run_date(self, token: str, url: str, last_run_date: datetime, end_date: datetime):
        events = []
        has_more_events = True
        current_page = 0

        while has_more_events:
            response = self.session.get(
                url,
                headers={
                    'Content-Type': 'application/json',
                    'Authorization': f'Bearer {token}'
                },
                params={
                    'startDate': last_run_date,
                    'endDate': end_date,
                    'page': current_page,
                    'pageSize': 1000
                }
            )

            if response.status_code != 200:
                raise CreditSafeMonitoringError(response)

            result = CreditSafeNotificationEventsResponse.from_json(response.json())

            for event in result.data:
                events.append(event)

            has_more_events = bool(result.paging.next)
            current_page += 1

        return events

    def _configure_events(self, token: str, portfolio_id: int):
        for country_code, event_configs in get_configure_event_payload().items():
            url = f'{self.base_url}/monitoring/portfolios/{portfolio_id}/eventRules/{country_code}'
            response = self.session.put(
                url,
                json=event_configs,
                headers={
                    'Content-Type': 'application/json',
                    'Authorization': f'Bearer {token}'
                }
            )

            if response.status_code != 204:
                raise CreditSafeMonitoringError(response)
