from enum import unique, Enum


@unique
class ErrorCode(Enum):
    INVALID_INPUT_DATA = 201
    PROVIDER_MISCONFIGURATION_ERROR = 205
    PROVIDER_CONNECTION_ERROR = 302
    PROVIDER_UNKNOWN_ERROR = 303
    UNKNOWN_INTERNAL_ERROR = 401


class MatchException(Exception):
    def __init__(self, message: str, raw_output: str = None):
        self.message = message
        self.raw_output = raw_output


class Error(object):

    @staticmethod
    def bad_api_request(e):
        return {
            'code': ErrorCode.INVALID_INPUT_DATA.value,
            'source': 'API',
            'message': 'Bad API request',
            'info': e.to_primitive()
        }
