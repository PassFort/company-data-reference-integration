
def make_error_response(errors=[]):
    return {
        'output_data': None,
        'raw': None,
        'errors': errors
    }


def make_screening_started_response(case_system_id, errors=[]):
    return {
        'output_data': {
            'worldcheck_system_id': case_system_id
        },
        'raw': None,
        'errors': errors
    }


def make_screening_results_response(errors=[], results=[]):
    return {
        'output_data': [],  # TODO Format the result
        'raw': [r.to_dict() for r in results],
        'errors': errors
    }
