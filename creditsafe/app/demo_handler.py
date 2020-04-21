from .api.types import SearchInput, ReportInput
from .api.internal_types import CreditSafeCompanyReport
from .file_utils import get_response_from_file
from demo_data.global_report_generator import get_report


class DemoHandler:

    def get_name_to_return(self, demo_creditsafe_id, country):
        if country == 'GBR':
            return {
                'pass': 'PASSFORT LIMITED',
                'partial': 'PASSFORT PARTIAL LIMITED',
                'partial_financial': 'PASSFORT PARTIAL FINANCIAL'
            }.get(demo_creditsafe_id)
        return {
            'pass': 'Aerial Traders',
            'partial': 'Aerial Traders PARTIAL',
            'partial_financial': 'Aerial Traders PARTIAL FINANCIAL'
        }.get(demo_creditsafe_id)

    def search(self, input_data: 'SearchInput'):
        search_query = (input_data.query or input_data.name or '').lower()
        if 'fail' in search_query:
            return []

        creditsafe_id = 'pass'

        if 'partial' in search_query:
            creditsafe_id = 'partial'

        if 'partial_financial' in search_query:
            creditsafe_id = 'partial_financial'

        result = {
            'name': self.get_name_to_return(creditsafe_id, input_data.country),
            'number': '09565115' if input_data.country == 'GBR' else '5560642554',
            'creditsafe_id': creditsafe_id,
            'country_of_incorporation': input_data.country
        }

        return [result]

    def get_report(self, input_data: 'ReportInput'):
        if input_data.country_of_incorporation == 'GBR':
            raw_report = get_response_from_file('passfort', folder='demo_data/reports')
        else:
            raw_report = get_report(input_data.creditsafe_id, input_data.country_of_incorporation)

        report = CreditSafeCompanyReport.from_json(raw_report['report'])

        formatted_report = report.as_passfort_format_41()

        if input_data.creditsafe_id == 'partial':
            formatted_report['metadata']['number'] = '1111111' # just return a different number
        if input_data.creditsafe_id == 'partial_financial':
            formatted_report['financials'] = None
        formatted_report['metadata']['name'] = self.get_name_to_return(
            input_data.creditsafe_id, input_data.country_of_incorporation)
        return formatted_report
