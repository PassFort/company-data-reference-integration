from typing import Tuple, Optional
from enum import Enum
from flask.json import JSONEncoder

from datetime import datetime
from dateutil import parser as dateutil_parser

import json
import re


class CustomJSONEncoder(JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Enum):
            return obj.value
        if isinstance(obj, datetime):
            return obj.strftime('%Y-%m-%d')
        if hasattr(obj, 'to_dict'):
            return obj.to_dict()

        return JSONEncoder.default(self, obj)


class BaseObject:
    def to_dict(self):
        return self.__dict__

    def serialize(self):
        return json.dumps(self, cls=CustomJSONEncoder)


class EntityType(Enum):
    INDIVIDUAL = 'INDIVIDUAL'
    COMPANY = 'COMPANY'


def name_strip(name: str) -> str:
    '''Clean names from useless garbage text'''
    garbage = ['via its funds']
    for string in garbage:
        if string in name:
            name = re.sub(string, '', name)
    return name


def format_names(
        firstname: Optional[str],
        lastname: Optional[str],
        fullname: Optional[str],
        entity_type: EntityType,
) -> Tuple[str, str]:
    if not firstname and not lastname:
        if fullname:
            fullname = name_strip(fullname)
            if entity_type == EntityType.INDIVIDUAL:
                names = fullname.split(' ')
                # First element is the title
                return ' '.join(names[1:-1]), names[-1]
            else:
                return '', fullname
        else:
            return '', ''
    else:
        return name_strip(firstname) if firstname else '', name_strip(lastname) if lastname else ''


def format_date(input_string: Optional[str]) -> Optional[datetime]:
    if input_string:
        try:
            return dateutil_parser.parse(input_string)
        except (ValueError, AttributeError, KeyError):
            pass

    return None
