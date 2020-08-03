from datetime import datetime
from enum import Enum, unique

from flask import Response


@unique
class ErrorCode(Enum):
    INVALID_INPUT_DATA = 201
    PROVIDER_MISCONFIGURATION_ERROR = 205
    PROVIDER_CONNECTION_ERROR = 302
    PROVIDER_UNKNOWN_ERROR = 303
    UNKNOWN_INTERNAL_ERROR = 401


class LoqateException(Exception):
    def __init__(self, response: Response):
        self.response = response


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
            'message': 'Connection error when contacting Loqate',
            'info': {
                'raw': '{}'.format(e)
            }
        }

    @staticmethod
    def provider_misconfiguration_error(e):
        return {
            'code': ErrorCode.PROVIDER_MISCONFIGURATION_ERROR.value,
            'source': 'PROVIDER',
            'message': f"Provider Configuration Error: '{e}' while running the 'Loqate' service",
            'info': {
                "Provider": "Loqate",
                "Timestamp": str(datetime.now())
            }
        }

    @staticmethod
    def provider_unknown_error(e):
        return {
            'code': ErrorCode.PROVIDER_UNKNOWN_ERROR.value,
            'source': 'PROVIDER',
            'message': e or 'There was an error calling Loqate',
            'info': {
                "Provider": "Loqate",
                "Timestamp": str(datetime.now())
            }
        }

    @staticmethod
    def from_exception(e):
        return {
            'code': ErrorCode.UNKNOWN_INTERNAL_ERROR.value,
            'source': 'ENGINE',
            'message': '{}'.format(e)
    }
