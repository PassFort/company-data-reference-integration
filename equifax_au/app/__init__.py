from flask import Flask
from flask_restful import Api

import api

def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'm14j826h87wfr4deb249ma4a6i8b78q0b'

    flask_api = Api(app)
    api.init_app(flask_api)

    return app