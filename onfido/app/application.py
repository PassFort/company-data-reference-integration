import os
import logging
from raven.contrib.flask import Sentry
from flask import Flask, jsonify, request
from onfido.onfido_requests import create_applicant, make_onfido_requestor, create_identity_check
from onfido.ekyc import onfido_check_to_individual, stage_error_from_onfido_response
from app.demo_handler import get_demo_ekyc_response, get_demo_watchlist_response

app = Flask(__name__)


sentry_url = os.environ.get('SENTRY_URL')
if sentry_url:
    sentry = Sentry(
        app,
        logging=True,
        level=logging.ERROR, dsn=sentry_url
    )


@app.route('/health')
def health():
    return jsonify('success')


@app.route('/ekyc-check', methods=['POST'])
def ekyc_check():
    json = request.json
    input_data = json['input_data']
    api_key = json['credentials']['token']
    is_demo = json['is_demo']
    use_dob = json['config'].get('use_dob', False)
    if is_demo:
        demo_data = get_demo_ekyc_response(input_data['personal_details']['name']['v'], use_dob)
        return jsonify(demo_data)

    requestor = make_onfido_requestor(api_key)
    logging.info('Fetch applicant')
    applicant_status, created_applicant = create_applicant(requestor, input_data)
    if applicant_status < 400:
        logging.info({'message': 'applicant request successful', 'response': created_applicant})
        # Make the check
        check_status, created_check = create_identity_check(requestor, created_applicant['id'])
        logging.info('Fetch check')
        if check_status < 400:
            logging.info({'message': 'Check successful', 'response': created_check})
            return jsonify(
                output_data=onfido_check_to_individual(created_applicant, created_check, use_dob),
                raw={'applicant': created_applicant, 'check': created_check},
                errors=[],
                price=0,
            )
        else:
            logging.info('Check request failed %s', created_check)
            errors = [stage_error_from_onfido_response(created_check, 'Check creation request failed')]
            return jsonify(
                raw={'applicant': created_applicant, 'check': created_check},
                errors=errors,
                price=0,
            )
    else:
        logging.info('Applicant request failed %s', created_applicant)
        errors = [stage_error_from_onfido_response(created_applicant, 'Applicant creation request failed')]
        return jsonify(
            raw={'applicant': created_applicant},
            errors=errors,
            price=0,
        )


@app.route('/watchlist', methods=['POST'])
def watchlist_check():
    json = request.json
    input_data = json['input_data']
    is_demo = json['is_demo']

    if is_demo:
        return jsonify(get_demo_watchlist_response(input_data['personal_details']['name']['v']))
