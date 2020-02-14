from dataclasses import dataclass
from requests.exceptions import HTTPError


class CifasConnectionError(Exception):
    pass


class CifasHTTPError(Exception):
    def __init__(self, http_error: HTTPError):
        self.http_error = http_error


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
