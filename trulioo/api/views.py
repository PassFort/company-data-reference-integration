from flask_restful import Resource
from flask import request
from json import JSONDecodeError
from requests.exceptions import HTTPError, ConnectTimeout
import pycountry

from api.demo_response import create_demo_response

from trulioo.api import validate_authentication
from trulioo.api import verify
from trulioo.convert_data import passfort_to_trulioo_data, trulioo_to_passfort_data, make_error

UNSUPPORTED_COUNTRY_MSG = 'Account not configured for this country'


def interpret_http_error(error, country_code):
    raw = error.response.text
    try:
        json = error.response.json()
        if json == UNSUPPORTED_COUNTRY_MSG or json.get('Message') == UNSUPPORTED_COUNTRY_MSG:
            alpha_3 = pycountry.countries.get(alpha_2=country_code).alpha_3
            error = make_error(
                code=106,
                message=f"Country '{alpha_3}' is not supported by the provider for this stage",
                info={
                    'country': alpha_3,
                    'original_error': raw,
                },
            )
            return error, raw
    except (AttributeError, JSONDecodeError):
        pass

    error = make_error(
        code=303,
        message='Unknown provider error',
        info={
            'original_error': raw,
        },
    )
    return error, raw


class Ekyc_check(Resource):

    def post(self):
        request_json = request.json
        if not request_json:
            response_body = {
                "decision": "ERROR",
                "output_data": {
                },
                "raw": {},
                "errors": [
                    {
                        'code': 201,
                        'message': 'The submitted data was invalid'
                    }
                ]
            }
            return response_body
        if not (request_json.get('credentials') and
                request_json['credentials'].get('username') and
                request_json['credentials'].get('password')):

            response_body = {
                "decision": "ERROR",
                "output_data": {
                },
                "raw": {},
                "errors": [
                    {
                        'code': 203,
                        'message': 'Missing provider credentials'
                    }
                ]
            }
            return response_body

        username = request_json['credentials']['username']
        password = request_json['credentials']['password']

        if request_json.get('is_demo'):
            passfort_to_trulioo_data(request_json)
            response = create_demo_response(request_json)
        else:
            trulioo_request_data, country_code, address_fields = passfort_to_trulioo_data(
                request_json)
            try:
                trulioo_response_data = verify(
                    username, password, country_code, trulioo_request_data)
                response = trulioo_to_passfort_data(
                    address_fields, trulioo_response_data)
            except ConnectTimeout:
                return {
                    'decision': 'ERROR',
                    'output_data': {},
                    'errors': [make_error(
                        code=302,
                        message="Provider Error: connection to 'Trulioo' service timed out",
                        info={
                            'original_error': raw,
                        },
                    )],
                }
            except HTTPError as exception:
                error, raw = interpret_http_error(exception, country_code)
                return {
                    'decision': 'ERROR',
                    'output_data': {},
                    'raw': raw,
                    'errors': [error],
                }

        return response


class HealthCheck(Resource):
    def get(self):
        return 'success', 200


def init_app(api):
    api.add_resource(Ekyc_check, '/ekyc-check')
    api.add_resource(HealthCheck, '/health')
