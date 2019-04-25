import json
from .api.mock_data.demo_responses import get_demo_work_visa, get_demo_study_visa, \
    get_demo_no_visa_response, get_demo_not_found_response
from .api.output_types import VSureVisaCheckResponse, VisaCheck


def get_demo_response(visa_holder: 'VisaHolderData', visa_check_type='WORK'):

    if 'NO_VISA' in visa_holder.given_names or 'NO_VISA' in visa_holder.family_name:
        return get_demo_no_visa_response(visa_holder)

    if 'NOT_FOUND' in visa_holder.given_names or 'NOT_FOUND' in visa_holder.family_name:
        return get_demo_not_found_response(visa_holder)

    if 'EXPIRED' in visa_holder.given_names or 'EXPIRED' in visa_holder.family_name:
        expiry_date = '22 Oct 2010'
    elif 'NO_EXPIRY' in visa_holder.given_names or 'NO_EXPIRY' in visa_holder.family_name:
        expiry_date = 'N/A'
    else:
        expiry_date = '22 Oct 2030'

    if visa_check_type == 'work':
        return get_demo_work_visa(visa_holder, expiry_date)
    elif visa_check_type == 'study':
        return get_demo_study_visa(visa_holder, expiry_date)
