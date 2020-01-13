from flask_restful import Resource
from flask import request

from api.demo_response import create_demo_response

from lexisnexis.api import echo_test_request
from lexisnexis.convert_data import passfort_to_lexisnexis_data, lexisnexis_to_passfort_data
from lexisnexis.api import verify


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
                        'message': 'INVALID_INPUT_DATA'
                    }
                ]
            }
            return response_body
        if not (request_json.get('credentials') and
                request_json['credentials'].get('username') and
                request_json['credentials'].get('password') and
                request_json['credentials'].get('url')):
            response_body = {
                "output_data": {
                },
                "raw": {},
                "errors": [
                    {
                        'code': 203,
                        'message': 'MISSING_API_KEY'
                    }
                ]
            }
            return response_body

        if request_json.get('is_demo'):
            response = create_demo_response(request_json)
        else:
            lexisnexis_request_data = passfort_to_lexisnexis_data(request_json)
            lexisnexis_response_data = verify(lexisnexis_request_data, request_json['credentials'])
            response = lexisnexis_to_passfort_data(lexisnexis_response_data)

        return response


class HealthCheck(Resource):
    def get(self):
        return 'ok'

    def post(self):
        request_json = request.json
        if not request_json:
            return 'ok'

        if not (request_json.get('credentials') and
                request_json['credentials'].get('username') and
                request_json['credentials'].get('password') and
                request_json['credentials'].get('url')):
            return 'MISSING_API_KEY', 203

        status_code = echo_test_request(request_json['credentials'])
        return 'LexisNexis Integration', status_code


def init_app(api):
    api.add_resource(Ekyc_check, '/ekyc-check')
    api.add_resource(HealthCheck, '/health')
