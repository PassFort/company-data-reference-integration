from .api.types import CheckInput
from .file_utils import get_response_from_file

class DemoHandler:
    def run_check(self, input_data: 'CheckInput'):
        passfort_report = get_response_from_file('passfort', folder='demo_data/reports')
        
        # TODO
        pass
