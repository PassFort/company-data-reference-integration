from dataclasses import dataclass
from requests.exceptions import HTTPError
from zeep.helpers import serialize_object


class CifasConnectionError(Exception):
    pass


class CifasHTTPError(Exception):
    def __init__(self, http_error: HTTPError):
        self.http_error = http_error


class CifasFaultError(Exception):
    def __init__(self, raw_obj: object):
        self.raw_obj = raw_obj


@dataclass
class Error:
    code: int
    message: str
    info: dict

    @classmethod
    def connection_error(self, error: Exception):
        return Error(
            code=302,
            message="Provider Error: connection to 'Cifas' service failed",
            info={
                'original_error': str(error),
            },
        )

    @classmethod
    def provider_error(self, error: CifasHTTPError):
        return Error(
            code=303,
            message='Unknown provider error',
            info={
                'original_error': error.http_error.response.text
            },
        )

    @classmethod
    def provider_validation_error(self, error: CifasFaultError):
        err_dict = serialize_object(error.raw_obj)

        err_value = err_dict.get('Value')
        err_message = err_dict.get('Error')
        err_elem = err_dict.get('Element')
        err_text = ''

        original_error = {k: error.raw_obj[k] for k in error.raw_obj}

        if err_value and err_message and err_elem:
            err_text = f': {err_message} Value: {err_value} Element: {err_elem}'
        return Error(
            code=303,
            message=f'Cifas validation error{err_text}',
            info={
                'original_error': original_error
            },
        )
