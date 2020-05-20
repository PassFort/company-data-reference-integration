from flask import Flask
from flask_restful import Api

import api

def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'd9b8a7279f1ff8a8dcba7faabeeb25a788507bab'

    flask_api = Api(app)
    api.init_app(flask_api)

    return app