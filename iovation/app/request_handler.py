import base64
import requests

from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry

from .api.types import IovationCheckError, IovationOutput, IovationCheckResponse, CheckInput, IovationCredentials

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


class IovationHandler:

    def __init__(self, credentials: IovationCredentials):
        if credentials.get('use_test_environment'):
            self.base_url = 'https://ci-api.iovation.com/fraud/v1'
        else:
            self.base_url = 'https://api.iovation.com/fraud/v1'
        self.credentials = credentials
        self.session = requests_retry_session()

    def is_test_environment(self):
        return self.credentials.get('use_test_environment', False)

    def run_check(self, input_data: CheckInput):
        token = self.get_authorization_token()

        response = self.session.post(
            f'{self.base_url}/subs/{self.credentials.subscriber_id}/checks',
            json=input_data.as_iovation_device_data().to_primitive(),
            headers={
                'Content-Type': 'application/json',
                'Authorization': f'Basic {token}'
            }
        )

        if response.status_code != 200:
            raise IovationCheckError(response)

        response = response.json()
        raw_data, output = IovationOutput.from_json(response)

        return raw_data, IovationCheckResponse.from_iovation_output(output, input_data.device_metadata, self.is_test_environment())

    def get_authorization_token(self):
        token = f'{self.credentials["subscriber_id"]}/{self.credentials["subscriber_account"]}:{self.credentials["password"]}'

        return base64.b64encode(token.encode('utf-8')).decode('utf-8')
