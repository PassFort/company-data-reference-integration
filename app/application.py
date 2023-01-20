from flask import Flask, request

from app.api.monitored_polling import monitored_polling_api
from app.api.one_time_sync import one_time_sync_api

# If `entrypoint` is not defined in app.yaml, App Engine will look for an app
# called `app` in `main.py`.
app = Flask(__name__)
app.register_blueprint(one_time_sync_api)
app.register_blueprint(monitored_polling_api)


@app.before_request
def pre_request_logging():
    request_data = "\n" + request.data.decode("utf8")
    request_data = request_data.replace("\n", "\n    ")

    app.logger.info(f"{request.method} {request.url}{request_data}")


@app.after_request
def post_request_logging(response):
    if response.direct_passthrough:
        response_data = "\n(direct pass-through)"
    else:
        response_data = "\n" + response.data.decode("utf8")
    response_data = response_data.replace("\n", "\n    ")

    app.logger.info(f"{response.status} {request.url}{response_data}")
    return response
