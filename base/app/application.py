import os
import logging
from flask import Flask
from raven.contrib.flask import Sentry

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
