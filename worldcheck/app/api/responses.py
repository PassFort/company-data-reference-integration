
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


def make_results_response(results=[], config=None):
    from swagger_client.models import MatchStrength
    from app.api.formatter import result_to_passfort_format
    order_of_strength = {
        MatchStrength.WEAK: 0,
        MatchStrength.MEDIUM: 1,
        MatchStrength.STRONG: 2,
        MatchStrength.EXACT: 3
    }
    minimum_order_of_strength = order_of_strength.get(config.minimum_match_strength, 0) if config else 0

    def meets_minimum_match_strength(match_strength):
        if match_strength is None:
            return True
        return order_of_strength.get(match_strength, 100) >= minimum_order_of_strength

    return {
        'output_data': [
            result_to_passfort_format(r)
            for r in results
            if meets_minimum_match_strength(r.match_strength)],
        'raw': [r.to_dict() for r in results],
        'errors': []
    }


def make_match_response(result):
    from app.api.formatter import entity_to_passfort_format
    return {
        'output_data': entity_to_passfort_format(result),
        'raw': result.to_dict(),
        'errors': []
    }
