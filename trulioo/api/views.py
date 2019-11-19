from flask_restful import Resource
from flask import request
from requests.exceptions import HTTPError, ConnectTimeout

from api.demo_response import create_demo_response

from trulioo.api import validate_authentication
from trulioo.api import verify
from trulioo.convert_data import passfort_to_trulioo_data, trulioo_to_passfort_data, make_error


class Ekyc_check(Resource):

    def post(self):
        request_json = request.json
        if not request_json:
            response_body = {
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
            trulioo_request_data, country_code = passfort_to_trulioo_data(
                request_json)
            try:
                trulioo_response_data = verify(
                    username, password, country_code, trulioo_request_data)
                response = trulioo_to_passfort_data(
                    trulioo_request_data, trulioo_response_data)
            except ConnectTimeout:
                return {
                    'output_data': {},
                    'errors': [make_error(
                        code=302,
                        message='Provider connection error',
                        info={
                            'raw': raw,
                        },
                    )],
                }
            except HTTPError as error:
                raw = error.response.text
                return {
                    'output_data': {},
                    'raw': raw,
                    'errors': [make_error(
                        code=303,
                        message='Unknown provider error',
                        info={
                            'raw': raw,
                        },
                    )],
                }

        return response


class HealthCheck(Resource):
    def get(self):
        return 'success', 200


def init_app(api):
    api.add_resource(Ekyc_check, '/ekyc-check')
    api.add_resource(HealthCheck, '/health')
