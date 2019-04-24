import json
from .api.mock_data.demo_responses import get_demo_work_visa, get_demo_study_visa, \
    get_demo_no_visa_response
from .api.output_types import VSureVisaCheckResponse, VisaCheck


def get_demo_response(individual_data: 'IndividualData', config: 'VSureConfig'):

    visa_holder = individual_data.as_visa_holder_data()

    demo_output = get_demo_output(visa_holder)

    raw_response, response_model = VSureVisaCheckResponse.from_json(demo_output)

    visa_check = VisaCheck.from_visa_check_response(response_model, config.visa_check_type)

    return {
        'raw_output': raw_response,
        'output_data': visa_check.to_primitive()
    }


def get_demo_output(visa_holder):

    if visa_holder.given_names.contains('NO_VISA') or visa_holder.family_name.contains('NO_VISA'):
        return get_demo_no_visa_response(visa_holder)

    if visa_holder.given_names.contains('NOT_FOUND') or visa_holder.family_name.contains('NOT_FOUND'):
        return get_demo_not_found_response(visa_holder)

    if visa_holder.given_names.contains('EXPIRED') or visa_holder.family_name.contains('EXPIRED'):
        expiry_date = '22 Oct 2010'
    elif visa_holder.given_names.contains('NO_EXPIRY') or visa_holder.family_name.contains('NO_EXPIRY'):
        expiry_date = 'N/A'

    if config.visa_check_type == 'WORK':
        demo_output = get_demo_work_visa(visa_holder, expiry_date)
    elif config.visa_check_type == 'STUDY':
        demo_output = get_demo_study_visa(visa_holder, expiry_date)
