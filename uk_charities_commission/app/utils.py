import requests
from datetime import datetime
from requests.exceptions import RequestException, HTTPError
from passfort_data_structure.entities.entity_type import EntityType


class UKCharitiesCommissionException(Exception):
    def to_dict(self):
        return {'message': self.args[0]}


# TODO - use this
class UKCharitiesCommissionAuthException(UKCharitiesCommissionException):
    pass


def handle_error(msg, custom_data=None):
    exception = UKCharitiesCommissionException(msg)

    try:
        from app.application import sentry

        print(exception)

        sentry.captureException(
            exc_info=(exception.__class__, exception, exception.__traceback__),
            extra=custom_data
        )
    except ImportError:
        pass


def permissive_string_compare(s1, s2):
    '''
    Compare strings, ignoring whitespace/capitalisaton/punctuation, and 0-padding
    the strings to be identical in length
    '''
    import string

    if (s1 is None) or (s2 is None):
        return False

    remove = string.punctuation + string.whitespace + '&'
    translation = str.maketrans('', '', remove)

    s1 = s1.translate(translation).upper()
    s2 = s2.translate(translation).upper()

    s1 = s1.zfill(len(s2))
    s2 = s2.zfill(len(s1))

    return s1 == s2


def parse_int(s):
    if s is None:
        return None

    try:
        return int(s)
    except ValueError as e:
        handle_error(f'Error parsing int: "{s}"')
        return None


def parse_date(date_str):
    if date_str is None:
        return None

    date = None

    try:
        date = datetime.strptime(date_str, '%d/%m/%Y %H:%M:%S')
    except ValueError:
        try:
            date = datetime.strptime(date_str, '%d/%m/%Y')
        except ValueError:
            handle_error(f'Error parsing date: "{date_str}"')
            return None

    return date.date().isoformat()


def is_active(charity):
    if charity.OrganisationType == 'R':
        return True
    elif charity.OrganisationType == 'RM':
        return False
    return None
