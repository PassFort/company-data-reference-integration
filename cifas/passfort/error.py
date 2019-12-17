from dataclasses import dataclass, field
from requests.exceptions import HTTPError


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
    def provider_error(self, error: HTTPError):
        return Error(
            code=303,
            message='Unknown provider error',
            info={
                'original_error': error.response.text
            },
        )

