import requests
from datetime import datetime
from requests.exceptions import RequestException, HTTPError
from passfort_data_structure.entities.entity_type import EntityType


class UKCharitiesCommissionAuthException(Exception):
    pass


class UKCharitiesCommissionException(Exception):
    pass

    def to_dict(self):
        return {'message': self.args[0]}


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


def string_compare(s1, s2):
    import string

    if (s1 is None) or (s2 is None):
        return False

    remove = string.punctuation + string.whitespace + '&'
    translation = str.maketrans('', '', remove)
    return s1.translate(translation).upper() == s2.translate(translation).upper()


def make_get(data):
    def inner(fields, *args, strip=False):
        if type(fields) is not list:
            return inner([fields], *args, strip=strip)

        try:
            value = None
            value = data
            for field in fields:
                value = value[field]

            if strip:
                value = value.strip()

            return value

        except (KeyError, IndexError, AttributeError):
            if len(args) > 0:
                return args[0]

            raise

    return inner


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


