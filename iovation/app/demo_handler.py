from .api.types import CheckInput, IovationCheckResponse, IovationOutput
from .file_utils import get_response_from_file

class DemoHandler:
    def run_check(self, input_data: 'CheckInput'):
        token = input_data.device_metadata.token.upper()
        if 'FAIL' in token:
            response = get_response_from_file('deny_result', folder='demo_data')
        elif 'REFER' in token:
            response = get_response_from_file('review_result', folder='demo_data')
        else:
            response = get_response_from_file('allow_result', folder='demo_data')

        raw_data, output = IovationOutput.from_json(response)

        response = IovationCheckResponse.from_iovation_output(output, input_data.device_metadata)
        return raw_data, response
