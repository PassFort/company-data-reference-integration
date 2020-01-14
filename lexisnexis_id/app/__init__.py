from os import environ

from flask import Flask
from flask_restful import Api
import sentry_sdk
from sentry_sdk.integrations.flask import FlaskIntegration

import api


def create_app():
    dsn = environ.get("SENTRY_URL")
    if dsn:
        sentry_sdk.init(
            dsn=dsn,
            integrations=[FlaskIntegration()]
        )

    app = Flask(__name__)
    app.config['SECRET_KEY'] = 'e10126b88efe4deb7494aba648b787fe'

    flask_api = Api(app)
    api.init_app(flask_api)

    return app
