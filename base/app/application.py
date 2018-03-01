import os
import logging
from flask import Flask
from raven.contrib.flask import Sentry
import app.json_logger

app = Flask(__name__)

sentry_url = os.environ.get('SENTRY_URL')
if sentry_url:
    sentry = Sentry(
        app,
        logging=True,
        level=logging.ERROR, dsn=sentry_url
    )


@app.route('/')
def main():
    return 'hello'
