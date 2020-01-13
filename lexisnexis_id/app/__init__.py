from flask import Flask
from flask_restful import Api

import api

def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'e10126b88efe4deb7494aba648b787fe'

    flask_api = Api(app)
    api.init_app(flask_api)

    return app