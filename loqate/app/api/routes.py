import logging
import os
from flask import request


def init_app(app):
    @app.route("/health", methods=['GET'])
    def health():
        return "ok"

    @app.route("/check", methods=['POST'])
    def addressCheck():
        request_json = request.json
        if not request_json:
            return {
                "output_data": {},
                "raw": {},
                "errors": [
                    {
                        'code': 201,
                        'message': 'INVALID_INPUT_DATA',
                    }
                ]
            }

        credentials = request_json.get('credentials', {})
        apikey = credentials.get('apikey')

        config = request_json.get('config')
        use_certified_dataset = request_json.get('use_certified_dataset')

        if not (apikey and len(apikey)):
            return {
                "output_data": {},
                "raw": {},
                "errors": [
                    {
                        'code': 203,
                        'message': 'MISSING_API_KEY',
                    }
                ]
            }
        return '', 400
