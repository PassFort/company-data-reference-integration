import os
import logging
import traceback

from flask import Flask, jsonify
from raven.contrib.flask import Sentry
from requests.exceptions import ConnectionError, Timeout

from .api.types import validate_model, CreditSafeSearchRequest, CreditSafeAuthenticationError, \
    CreditSafeSearchError, CreditSafeReportError, ErrorCode, Error, CreditSafeCompanyReportRequest, \
    CreditSafePortfolioRequest, CreditSafeMonitoringError, CreditSafeMonitoringRequest, \
    CreditSafeMonitoringEventsRequest
from .api.internal_types import CreditSafeNotificationEventsResponse
from .request_handler import CreditSafeHandler
from .demo_handler import DemoHandler


app = Flask(__name__)

logging.getLogger().setLevel(logging.INFO)


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
    app.dd.increment('passfort.services.creditsafe.api_call', tags=tags)
    return response


@app.route('/health')
def health():
    return jsonify('success')


@app.route('/search', methods=['POST'])
@validate_model(CreditSafeSearchRequest)
def search(request_data: 'CreditSafeSearchRequest'):
    if request_data.is_demo:
        demo_handler = DemoHandler()
        companies = demo_handler.search(request_data.input_data)
        return jsonify({
            'output_data': companies,
            'raw_data': {},
            'errors': []
        })

    handler = CreditSafeHandler(request_data.credentials)
    raw, companies = handler.search(request_data.input_data, fuzz_factor=90)
    return jsonify({
        'output_data': companies,
        'raw_data': raw,
        'errors': []
    })


@app.route('/company_report', methods=['POST'])
@validate_model(CreditSafeCompanyReportRequest)
def company_report(request_data: 'CreditSafeCompanyReportRequest'):
    if request_data.is_demo:
        demo_handler = DemoHandler()
        report = demo_handler.get_report(request_data.input_data)
        return jsonify({
            'output_data': report,
            'raw_data': {},
            'errors': []
        })

    handler = CreditSafeHandler(request_data.credentials)
    raw, report = handler.get_report_41(request_data.input_data)
    return jsonify({
        'output_data': report,
        'raw_data': raw,
        'errors': []
    })


# Temporary endpoint to allow us to migrate to the 41 representation
@app.route('/4.1/company_report', methods=['POST'])
@validate_model(CreditSafeCompanyReportRequest)
def company_report_41(request_data: 'CreditSafeCompanyReportRequest'):
    if request_data.is_demo:
        demo_handler = DemoHandler()
        report = demo_handler.get_report(request_data.input_data)
        return jsonify({
            'output_data': report,
            'raw_data': {},
            'errors': []
        })

    handler = CreditSafeHandler(request_data.credentials)
    raw, report = handler.get_report_41(request_data.input_data)
    return jsonify({
        'output_data': report,
        'raw_data': raw,
        'errors': []
    })


@app.route('/monitoring_portfolio', methods=['POST'])
@validate_model(CreditSafePortfolioRequest)
def monitoring_portfolio(request_data: 'CreditSafePortfolioRequest'):
    handler = CreditSafeHandler(request_data.credentials)

    portfolio = handler.create_portfolio(request_data.portfolio_name)

    return jsonify({
        'portfolio_id': portfolio.id,
        'errors': []
    })


@app.route('/monitoring', methods=['POST'])
@validate_model(CreditSafeMonitoringRequest)
def monitor_company(request_data: 'CreditSafeMonitoringRequest'):
    handler = CreditSafeHandler(request_data.credentials)

    handler.monitor_company(request_data)
    return jsonify({})


@app.route('/monitoring_events', methods=['POST'])
@validate_model(CreditSafeMonitoringEventsRequest)
def get_monitoring_events(request_data: CreditSafeMonitoringEventsRequest):
    handler = CreditSafeHandler(request_data.credentials)

    handler.handle_events(request_data)

    return jsonify({})


@app.errorhandler(400)
def api_400(error):
    logging.error(error.description)
    return jsonify(errors=[error.description]), 400


@app.errorhandler(CreditSafeAuthenticationError)
def handle_auth_error(auth_error):
    response = auth_error.response
    response_content = response.json()

    if response.status_code == 401:
        return jsonify(
            raw=response_content,
            errors=[
                Error.provider_misconfiguration_error(response_content.get('message'))
            ]
        ), 200
    else:
        return jsonify(
            raw=response_content,
            errors=[
                # Yes, messages come from different fields
                # (messages, details, or error)
                Error.provider_unhandled_error(response_content.get('details'))
            ]
        ), 500


@app.errorhandler(CreditSafeSearchError)
def handle_search_error(search_error):
    response = search_error.response
    response_content = response.json()

    if response.status_code == 400:
        return jsonify(
            raw=response_content,
            errors=[
                # Yes, messages come from different fields
                # (messages, details, or error)
                Error.provider_unhandled_error(response_content.get('details'))
            ]
        ), 200
    else:
        logging.error(f'Creditsafe search error {response.status_code}: {response_content}')
        return jsonify(
            raw=response_content,
            errors=[
                # Yes, messages come from different fields
                # (messages, details, or error)
                Error.provider_unhandled_error(response_content.get('error') or 'Unknown error')
            ]
        ), 200


@app.errorhandler(CreditSafeReportError)
def handle_report_error(report_error):
    response = report_error.response
    response_content = response.json()

    if response.status_code == 400:
        return jsonify(
            raw=response_content,
            errors=[
                Error.provider_unhandled_error(response_content.get('details') or 'Report Unavailable')
            ]
        ), 200  # Clients could potentially change this ID? So surface the error
    elif response.status_code == 403 and 'Forbidden' in (response_content.get('message') or ''):
        return jsonify(
            raw=response_content,
            errors=[
                Error.provider_misconfiguration_error(
                    f"The request could not be authorised: {response_content.get('details')}")
            ]
        ), 200
    else:
        logging.error(f'Creditsafe report error {response.status_code}: {response_content}')
        return jsonify(
            raw=response_content,
            errors=[
                # Yes, messages come from different fields
                # (messages, details, or error)
                Error.provider_unhandled_error(response_content.get('error') or 'Unknown error')
            ]
        ), 200


@app.errorhandler(CreditSafeMonitoringError)
def handle_monitoring_error(monitoring_error):
    response = monitoring_error.response
    response_content = response.json()

    if response.status_code == 400 or response.status_code == 404:
        return jsonify(
            raw=response_content,
            errors=[
                Error.provider_unhandled_error(response_content.get('message'))
            ]
        ), 200
    elif response.status_code == 403 and response_content.get('message') == 'Access forbidden':
        return jsonify(
            raw=response_content,
            errors=[
                Error.provider_misconfiguration_error(
                    f"The request could not be authorised: Access forbidden")
            ]
        )
    else:
        return jsonify(
            raw=response_content,
            errors=[
                Error.provider_unhandled_error(response_content.get('message'))
            ]
        ), 500


@app.errorhandler(ConnectionError)
def connection_error(error):
    logging.error(traceback.format_exc())
    return jsonify(errors=[
        {
            'code': ErrorCode.PROVIDER_CONNECTION_ERROR.value,
            'source': 'PROVIDER',
            'message': "Provider Error: connection to 'Creditsafe' service encountered an error."
        }
    ]), 200


@app.errorhandler(Timeout)
def timeout_error(error):
    logging.error(traceback.format_exc())
    return jsonify(errors=[
        {
            'code': ErrorCode.PROVIDER_CONNECTION_ERROR.value,
            'source': 'PROVIDER',
            'message': "Provider Error: connection to 'Creditsafe' service timed out"
        }
    ]), 200
