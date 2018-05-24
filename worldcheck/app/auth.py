import hmac
import hashlib
import base64
from datetime import datetime

from swagger_client import ApiClient


class CustomAuthApiClient(ApiClient):

    def __init__(self, gateway_host, api_key, api_key_secret, gateway_base_url='/v1'):
        super().__init__()
        self.gateway_host = gateway_host
        self.api_key = api_key
        self.api_key_secret = api_key_secret
        self.gateway_base_url = gateway_base_url
        self.configuration.host = "https://{}{}".format(self.gateway_host, self.gateway_base_url)

    def call_api(self, resource_path,
                 method,
                 path_params=None,
                 query_params=None,
                 header_params=None,
                 body=None, *args, **kwargs):

        auth_headers = self.generate_headers(resource_path, method, body)
        updated_headers = auth_headers if header_params is None else {**header_params, **auth_headers}
        return super().call_api(resource_path,
                                method,
                                path_params,
                                query_params,
                                updated_headers,
                                body,
                                *args, **kwargs)

    def generate_headers(self, resource_path, method, body):
        """
        Algorithm to generate the authorization headers was supplied by world check in their postman examples.

        :param resource_path: The specific api path
        :param method: one of GET, PUT, POST, HEAD, OPTIONS
        :param body: the content to be send (given as a model object)
        :return: dict: {Date, Authorization}
        """
        import json
        date = datetime.utcnow().strftime('%a, %d %B %Y %H:%M:%S GMT')
        data_to_sign = '(request-target): {method} {base}{path}\nhost: {host}\ndate: {date}'.format(
            method=method.lower(),
            base=self.gateway_base_url,
            path=resource_path,
            host=self.gateway_host,
            date=date
        )

        if body:
            content = json.dumps(self.sanitize_for_serialization(body))
            content_length = len(content)

            data_to_sign += '\ncontent-type: application/json\ncontent-length: {}\n{}'.format(content_length, content)

        hmac = self.generate_auth_header(data_to_sign)
        signature_extra_fields = " content-type content-length" if body else ""
        r = {
            'Date': date,
            'Authorization':
                'Signature keyId="{}",algorithm="hmac-sha256",'
                'headers="(request-target) host date{}",signature="{}"'.format(
                    self.api_key, signature_extra_fields, hmac.decode(),
                )
        }

        return r

    def generate_auth_header(self, data_to_sign):
        return base64.b64encode(
            hmac.new(
                self.api_key_secret.encode('utf-8'),
                msg=data_to_sign.encode('utf-8'),
                digestmod=hashlib.sha256
            ).digest())

