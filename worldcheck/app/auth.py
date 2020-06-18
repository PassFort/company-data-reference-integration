import hmac
import hashlib
import base64
import logging
import time
from datetime import datetime
from urllib3.exceptions import MaxRetryError

from swagger_client import ApiClient
import worldcheck_client_1_6


class CustomAuthApiClient(ApiClient):

    def __init__(self, gateway_host, api_key, api_key_secret, gateway_base_url='/v1'):
        super().__init__()
        self.gateway_host = gateway_host
        self.api_key = api_key
        self.api_key_secret = api_key_secret
        self.gateway_base_url = gateway_base_url
        self.configuration.host = "https://{}{}".format(self.gateway_host, self.gateway_base_url)

    def request(self, method, url, query_params=None, headers=None,
                post_params=None, body=None, _preload_content=True,
                _request_timeout=None):
        from app.worldcheck_handler import WorldCheckConnectionError
        from swagger_client.rest import ApiException

        path = url[len(self.configuration.host):]

        def auth_request():
            auth_headers = self.generate_headers(path, method, body)
            updated_headers = auth_headers if headers is None else {**headers, **auth_headers}

            logging.info(
                f'Sending authorized request ({method} {url}) with headers:\n{updated_headers}\nand body:\n{body}')

            return super(CustomAuthApiClient, self).request(
                method,
                url,
                query_params,
                updated_headers,
                post_params,
                body,
                _preload_content,
                30  # request_timeout
            )
        try:
            '''
            The underying library automatically retries connection errors 3 times. 
            If it still fails, it raises a MaxRetryError.

            429 codes are specific to worldcheck:

                The API client is making too many concurrent requests, and some are being throttled.
                Throttled requests can be retried (with an updated request Date and HTTP signature) after a short delay.
            '''
            try:
                return auth_request()
            except ApiException as e:
                '''
                Massive hack: sometimes when we retry after a delay, the "Date" header deviation is too great
                and our authentication fails. To avoid this, we retry the whole thing once with a freshly
                authenticated request.
                '''
                if e.status == 401:
                    return auth_request()
                else:
                    raise
        except MaxRetryError:
            raise WorldCheckConnectionError('Unable to connect to {}'.format(url))

    def generate_headers(self, resource_path, method, body):
        """
        Algorithm to generate the authorization headers was supplied by world check in their postman examples.

        :param resource_path: The specific api path
        :param method: one of GET, PUT, POST, HEAD, OPTIONS
        :param body: the content to be send (given as a model object)
        :return: dict: {Date, Authorization}
        """
        import json
        date = datetime.utcnow().strftime('%a, %d %b %Y %H:%M:%S GMT')
        data_to_sign = '(request-target): {method} {base}{path}\nhost: {host}\ndate: {date}'.format(
            method=method.lower(),
            base=self.gateway_base_url,
            path=resource_path,
            host=self.gateway_host,
            date=date
        )

        if body:
            content = json.dumps(body)
            content_length = len(content)

            data_to_sign += '\ncontent-type: application/json\ncontent-length: {}\n{}'.format(content_length, content)

        hmac = self.generate_auth_header(data_to_sign)
        signature_extra_fields = ' content-type content-length' if body else ''
        auth_headers = {
            'Date': date,
            'Authorization':
                'Signature keyId="{}",algorithm="hmac-sha256",'
                'headers="(request-target) host date{}",signature="{}"'.format(
                    self.api_key, signature_extra_fields, hmac.decode(),
                )
        }

        return auth_headers

    def generate_auth_header(self, data_to_sign):
        return base64.b64encode(
            hmac.new(
                self.api_key_secret.encode('utf-8'),
                msg=data_to_sign.encode('utf-8'),
                digestmod=hashlib.sha256
            ).digest())


class CustomAuthApiClient_1_6(worldcheck_client_1_6.ApiClient):

    def __init__(self, gateway_host, api_key, api_key_secret, gateway_base_url='/v1'):
        super().__init__()
        self.gateway_host = gateway_host
        self.api_key = api_key
        self.api_key_secret = api_key_secret
        self.gateway_base_url = gateway_base_url
        self.configuration.host = "https://{}{}".format(self.gateway_host, self.gateway_base_url)

    def request(self, method, url, query_params=None, headers=None,
                post_params=None, body=None, _preload_content=True,
                _request_timeout=None):
        from app.worldcheck_handler import WorldCheckConnectionError
        from worldcheck_client_1_6.rest import ApiException

        path = url[len(self.configuration.host):]

        def auth_request():
            auth_headers = self.generate_headers(path, method, body)

            updated_headers = auth_headers if headers is None else {**headers, **auth_headers}

            logging.info(
                f'Sending authorized request ({method} {url}) with headers:\n{updated_headers}\nand body:\n{body}')

            return super(CustomAuthApiClient_1_6, self).request(
                method,
                url,
                query_params,
                updated_headers,
                post_params,
                body,
                _preload_content,
                30  # request_timeout
            )
        try:
            '''
            The underying library automatically retries connection errors 3 times. 
            If it still fails, it raises a MaxRetryError.

            429 codes are specific to worldcheck:

                The API client is making too many concurrent requests, and some are being throttled.
                Throttled requests can be retried (with an updated request Date and HTTP signature) after a short delay.
            '''
            try:
                return auth_request()
            except ApiException as e:
                '''
                Massive hack: sometimes when we retry after a delay, the "Date" header deviation is too great
                and our authentication fails. To avoid this, we retry the whole thing once with a freshly
                authenticated request.
                '''
                if e.status == 401:
                    return auth_request()
                else:
                    raise
        except MaxRetryError:
            raise WorldCheckConnectionError('Unable to connect to {}'.format(url))

    def generate_headers(self, resource_path, method, body):
        """
        Algorithm to generate the authorization headers was supplied by world check in their postman examples.

        :param resource_path: The specific api path
        :param method: one of GET, PUT, POST, HEAD, OPTIONS
        :param body: the content to be send (given as a model object)
        :return: dict: {Date, Authorization}
        """
        import json
        date = datetime.utcnow().strftime('%a, %d %b %Y %H:%M:%S GMT')
        data_to_sign = '(request-target): {method} {base}{path}\nhost: {host}\ndate: {date}'.format(
            method=method.lower(),
            base=self.gateway_base_url,
            path=resource_path,
            host=self.gateway_host,
            date=date
        )

        if body:
            content = json.dumps(body)
            content_length = len(content)

            data_to_sign += '\ncontent-type: application/json\ncontent-length: {}\n{}'.format(content_length, content)

        hmac = self.generate_auth_header(data_to_sign)
        signature_extra_fields = ' content-type content-length' if body else ''
        auth_headers = {
            'Date': date,
            'Authorization':
                'Signature keyId="{}",algorithm="hmac-sha256",'
                'headers="(request-target) host date{}",signature="{}"'.format(
                    self.api_key, signature_extra_fields, hmac.decode(),
                )
        }

        return auth_headers

    def generate_auth_header(self, data_to_sign):
        return base64.b64encode(
            hmac.new(
                self.api_key_secret.encode('utf-8'),
                msg=data_to_sign.encode('utf-8'),
                digestmod=hashlib.sha256
            ).digest())
