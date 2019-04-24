from enum import unique, Enum

@unique
class ErrorCode(Enum):
    INVALID_INPUT_DATA = 201
    PROVIDER_CONNECTION_ERROR = 302
    PROVIDER_UNKNOWN_ERROR = 303
    UNKNOWN_INTERNAL_ERROR = 401


class VSureServiceException(Exception):
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

    @staticmethod
    def provider_connection_error(e):
        return {
            'code': ErrorCode.PROVIDER_CONNECTION_ERROR.value,
            'source': 'PROVIDER',
            'message': 'Connection error when contacting vSure',
            'info': {
                'raw': '{}'.format(e)
            }
        }

    @staticmethod
    def provider_unknown_error(e):
        return {
            'code': ErrorCode.PROVIDER_UNKNOWN_ERROR.value,
            'source': 'PROVIDER',
            'message': e.message or 'There was an error calling vSure',
            'info': {
                'raw': '{}'.format(e)
            }
        }

    @staticmethod
    def from_exception(e):
        return {
            'code': ErrorCode.UNKNOWN_INTERNAL_ERROR.value,
            'source': 'ENGINE',
            'message': '{}'.format(e)
        }
