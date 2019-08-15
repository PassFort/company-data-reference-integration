from flask import Flask
from flask_restful import Api

import api

def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = '6da2498d72b9c35a41c5f944m44321KL209d'

    flask_api = Api(app)
    api.init_app(flask_api)

    return app