from flask_restful import Resource
from flask import request

from api.demo_response import create_demo_response

from worldview.api import echo_test_request, verify
from worldview.convert_data import passfort_to_worldview_data, worldview_to_passfort_data

class BaseEkycResource(Resource):
    def is_credentials_valid(self, credentials):
        return credentials\
            and credentials.get('username')\
            and credentials.get('password')\
            and credentials.get('tenant')\
            and credentials.get('url')

class Ekyc_check(BaseEkycResource):
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

        if request_json.get('is_demo'):
            response = create_demo_response(request_json)
        else:
            if not self.is_credentials_valid(request_json.get('credentials')):
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

            worldview_request_data = passfort_to_worldview_data(request_json)
            worldview_response_data = verify(worldview_request_data, request_json['credentials'])

            # return worldview_response_data
            response = worldview_to_passfort_data(worldview_response_data)

        return response

class HealthCheck(BaseEkycResource):
    def get(self):
        return 'ok'

    def post(self):
        request_json = request.json
        if not request_json:
            return 'ok'

        if not self.is_credentials_valid(request_json.get('credentials')):
            return 'MISSING_API_KEY', 203

        status_code =  echo_test_request(request_json['credentials'])

        return 'Global Data Consortium Worldview Integration', status_code


def init_app(api):
    api.add_resource(Ekyc_check, '/ekyc-check')
    api.add_resource(HealthCheck, '/health-check')
