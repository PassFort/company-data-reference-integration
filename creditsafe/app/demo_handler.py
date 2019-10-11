from .api.types import SearchInput, ReportInput
from .api.internal_types import CreditSafeCompanyReport
from .file_utils import get_response_from_file

class DemoHandler:

    def search(self, input_data: 'SearchInput'):
        search_query = (input_data.query or input_data.name or '').lower()
        if 'fail' in search_query:
            return []

        creditsafe_id = 'pass'
        name = 'PASSFORT LIMITED'
        if 'partial' in search_query:
            creditsafe_id = 'partial'
            name = 'PASSFORT PARTIAL LIMITED'

        result = {
            'name': name,
            'number': '09565115',
            'creditsafe_id': creditsafe_id,
            'country_of_incorporation': 'GBR'
        }

        return [result]

    def get_report(self, input_data: 'ReportInput'):
        passfort_report = get_response_from_file('passfort', folder='demo_data/reports')
        report = CreditSafeCompanyReport.from_json(passfort_report['report'])

        formatted_report = report.as_passfort_format_41()

        if input_data.creditsafe_id == 'partial':
            formatted_report['metadata']['number'] = '1111111' # just return a different number
        return formatted_report
