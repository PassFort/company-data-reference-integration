from flask_restful import Resource
from flask import request

from api.demo_response import create_demo_response

from equifax.api import echo_test_request

from equifax.api import verify
from equifax.convert_data import passfort_to_equifax_data
from equifax.convert_data import equifax_to_passfort_data

IDMATRIX_URL = 'https://apiconnect.equifax.com.au/'
IDMATRIX_CTA_URL = 'https://ctaau.apiconnect.equifax.com.au/cta/'

class Ekyc_check(Resource):

    def post(self):
        request_json = request.json
        if not request_json:
            response_body = {
                "output_data": {
                    'decision': 'ERROR'
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
             (request_json['credentials'].get('username') and\
             request_json['credentials'].get('password') and\
             request_json['credentials'].get('is_cta') is not None)):

            response_body = {
                "output_data": {
                    'decision': 'ERROR'
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
            url = IDMATRIX_CTA_URL if request_json['credentials'].get('is_cta') else IDMATRIX_URL

            equifax_request_data = passfort_to_equifax_data(request_json)
            equifax_response_data = verify(equifax_request_data, url)

            response = equifax_to_passfort_data(equifax_response_data)

        return response

class HealthCheck(Resource):
    def get(self):
        return 'ok'

    def post(self):
        request_json = request.json
        if not request_json:
            return 'ok'

        if not (request_json.get('credentials') and\
             request_json['credentials'].get('username') and\
             request_json['credentials'].get('password') and\
             request_json['credentials'].get('is_cta') is not None):
            return 'MISSING_API_KEY', 203

        url = IDMATRIX_CTA_URL if request_json['credentials'].get('is_cta') else IDMATRIX_URL
        return echo_test_request(request_json['credentials'], url)


def init_app(api):
    api.add_resource(Ekyc_check, '/ekyc-check')
    api.add_resource(HealthCheck, '/health')
