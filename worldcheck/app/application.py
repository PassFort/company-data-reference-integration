import os
import logging
import traceback

import app.json_logger

from flask import Flask, jsonify, abort
from raven.contrib.flask import Sentry

from app.api.types import validate_model, ScreeningRequest, ScreeningResultsRequest, OngoingScreeningResultsRequest, \
    Error, OngoingScreeningDisableRequest
from app.api.responses import make_error_response
from app.worldcheck_handler import CaseHandler, MatchHandler, WorldCheckPendingError, WorldCheckConnectionError

from swagger_client.rest import ApiException
app = Flask(__name__)


class DataDogWrapper:
    def __init__(self, mock=True):
        self.mock = mock

    def increment(self, metric, value=1, tags=None, sample_rate=1):
        from datadog import statsd

        if self.mock:
            logging.info('Increment {} called with value {} and tags: {}'.format(metric, value, tags))
        else:
            try:
                statsd.increment(metric, value, tags, sample_rate)
            except Exception:
                logging.error('Statsd error when increment {} was '
                              'called with value {} and tags: {}'.format(metric, value, tags))


def initialize_datadog():
    from datadog import initialize

    try:
        initialize(statsd_host=os.environ['STATSD_HOST_IP'],
                   statsd_port=os.environ['STATSD_HOST_PORT'])
        return DataDogWrapper(mock=False)
    except Exception:
        return DataDogWrapper(mock=True)


app.dd = initialize_datadog()


sentry_url = os.environ.get('SENTRY_URL')
if sentry_url:
    sentry = Sentry(
        app,
        logging=True,
        level=logging.ERROR, dsn=sentry_url
    )


@app.after_request
def send_analytics(response):
    from flask import request
    tags = [
        'method:{}'.format(request.method),
        'endpoint:{}'.format(request.endpoint),
        'path:{}'.format(request.path),
        'full_path:{}'.format(request.full_path),
        'status_code:{}'.format(response.status_code)
    ]
    app.dd.increment('passfort.services.worldcheck.api_call', tags=tags)
    return response


@app.route('/health')
def health():
    return jsonify('success')


@app.route('/screening_request', methods=['POST'])
@validate_model(ScreeningRequest)
def screen_request(request_data: ScreeningRequest):
    result = CaseHandler(
        request_data.credentials,
        request_data.config,
        request_data.is_demo
    ).submit_screening_request(request_data.input_data)
    return jsonify(result)


@app.route('/results/<string:worldcheck_system_id>', methods=['POST'])
@validate_model(ScreeningResultsRequest)
def poll_results_request(request_data: ScreeningResultsRequest, worldcheck_system_id):
    try:
        case_handler = CaseHandler(
            request_data.credentials,
            request_data.config,
            request_data.is_demo
        )
        result = case_handler.get_results(worldcheck_system_id)

        if request_data.config.enable_ongoing_monitoring:
            case_handler.set_ongoing_screening(worldcheck_system_id)

        return jsonify(result)
    except WorldCheckPendingError:
        # The request has been accepted for processing,
        # but the processing has not been completed.
        return jsonify({}), 202


@app.route('/match/<string:match_id>', methods=['POST'])
@validate_model(ScreeningResultsRequest)
def get_match_data(request_data: ScreeningResultsRequest, match_id):
    return jsonify(MatchHandler(request_data.credentials, None, request_data.is_demo).get_entity_for_match(match_id))


@app.route('/match/<string:match_id>/associates', methods=['POST'])
@validate_model(ScreeningResultsRequest)
def get_match_associates(request_data: ScreeningResultsRequest, match_id):
    return jsonify(
        MatchHandler(
            request_data.credentials,
            None,
            request_data.is_demo
        ).get_match_associates(match_id)
    )


@app.route('/match/<string:match_id>/associate/<string:associate_id>', methods=['POST'])
@validate_model(ScreeningResultsRequest)
def get_associate_data(request_data: ScreeningResultsRequest, match_id, associate_id):
    return jsonify(
        MatchHandler(
            request_data.credentials,
            None,
            request_data.is_demo
        ).get_associate(match_id, associate_id)
    )


@app.route('/results/ongoing_monitoring', methods=['POST'])
@validate_model(OngoingScreeningResultsRequest)
def ongoing_monitoring_results_request(request_data: OngoingScreeningResultsRequest):
    from requests import RequestException

    result = CaseHandler(
            request_data.credentials, None, False
        ).get_ongoing_screening_results(request_data.from_date)

    try:
        send_to_callback(
            request_data.callback_url,
            {
                'institution_id': request_data.institution_id,
                'results': result
            }
        )
    except RequestException as e:
        return jsonify(errors=[Error.from_exception(e)]), 500
    return jsonify(errors=[])


@app.route('/config/ongoing_monitoring/<string:case_system_id>', methods=['DELETE'])
@validate_model(OngoingScreeningDisableRequest)
def disable_ongoing_monitoring_request(request_data: OngoingScreeningDisableRequest, case_system_id):
    return jsonify(
        CaseHandler(
            request_data.config,
            request_data.credentials,
        ).disable_ongoing_screening(case_system_id)
    )


def send_to_callback(callback_url, result):
    import requests
    import json
    response = requests.post(callback_url, json=result)
    response.raise_for_status()


@app.errorhandler(400)
def api_400(error):

    return jsonify(errors=[error.description]), 400


@app.errorhandler(500)
def api_500(error):
    logging.error(traceback.format_exc())
    return jsonify(errors=[Error.from_exception(error)]), 500


@app.errorhandler(WorldCheckConnectionError)
def api_provider_connection_error(error):
    logging.error(traceback.format_exc())
    return jsonify(errors=[Error.from_exception(error)]), 500


@app.errorhandler(ApiException)
def api_provider_other_error(error):
    logging.error(traceback.format_exc())
    return jsonify(make_error_response([Error.from_provider_exception(error)]))
