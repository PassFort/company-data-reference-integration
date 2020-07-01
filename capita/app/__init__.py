from flask import Flask
from flask_restful import Api

import api

def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'j19855fcace028a0f239c7af28315aa2a935ba86'

    flask_api = Api(app)
    api.init_app(flask_api)

    return app