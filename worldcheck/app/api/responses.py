import logging
from swagger_client.models import Entity, Associate


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

    minimum_order_of_strength = None
    if config:
        minimum_order_of_strength = order_of_strength.get(config.minimum_match_strength)
        if minimum_order_of_strength is None:
            logging.error('Unexpected minimum match strength: {}'.format(config.minimum_match_strength))

    def meets_minimum_match_strength(match_strength):
        if match_strength is None or minimum_order_of_strength is None:
            return True

        match_strength_order = order_of_strength.get(match_strength)
        if match_strength_order is None:
            logging.error('Unexpected match strength from provider: {}'.format(match_strength))
            return True

        return match_strength_order >= minimum_order_of_strength

    return {
        'output_data': [
            result_to_passfort_format(r)
            for r in results
            if meets_minimum_match_strength(r.match_strength)],
        'raw': [r.to_dict() for r in results],
        'errors': []
    }


def make_match_response(result):
    from app.api.formatter import entity_to_passfort_format, entity_to_events
    return {
        'output_data': entity_to_passfort_format(result),
        'raw': result.to_dict(),
        'errors': [],
        'events': entity_to_events(result)
    }


def make_associates_response(associates):

    return {
        'output_data': associates,
        'errors': []
    }


def make_associate_response(associate_data: Entity, association: Associate):
    from app.api.formatter import associated_entity_to_passfort_format
    return {
        'output_data': associated_entity_to_passfort_format(associate_data, association),
        'raw': {
            'associate_data': associate_data.to_dict(),
            'association': association.to_dict()
        },
        'errors': []
    }
