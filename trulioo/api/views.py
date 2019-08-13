from flask_restful import Resource
from flask import request

from api.demo_response import create_demo_response

from trulioo.api import validate_authentication
from trulioo.api import verify
from trulioo.convert_data import passfort_to_trulioo_data
from trulioo.convert_data import truilioo_to_passfort_data

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
        if not (request_json.get('credentials') and\
             request_json['credentials'].get('username') and\
             request_json['credentials'].get('password')):

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

        username = request_json['credentials']['username']
        password = request_json['credentials']['password']

        if request_json.get('is_demo'):
            response = create_demo_response(request_json)

        else:
            trulioo_request_data, country_code = passfort_to_trulioo_data(request_json)
            trulioo_response_data = verify(username, password, country_code, trulioo_request_data)

            response = truilioo_to_passfort_data(trulioo_response_data)

        return response

class HealthCheck(Resource):
    def post(self):
        request_json = request.json
        if not request_json:
            return 'INVALID_INPUT_DATA', 201
        if not (request_json.get('credentials') and\
             request_json['credentials'].get('username') and\
             request_json['credentials'].get('password')):
            return 'MISSING_API_KEY', 203
        
        status_code = validate_authentication(
            request_json['credentials'].get('username'),
            request_json['credentials'].get('password'))

        return 'Trulioo Integration', status_code


def init_app(api):
    api.add_resource(Ekyc_check, '/ekyc-check')
    api.add_resource(HealthCheck, '/health-check')
