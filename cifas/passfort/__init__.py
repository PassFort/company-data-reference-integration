from enum import Enum
from dataclasses import field
from dataclasses_json import config


class EntityType(Enum):
    INDIVIDUAL = 'INDIVIDUAL'
    COMPANY = 'COMPANY'


def decode_tagged_union(*dataclasses, tag='type'):
    tagged_classes = {}
    for cls in dataclasses:
        cls_tag = getattr(cls, tag)
        if isinstance(cls_tag, Enum):
            tagged_classes[cls_tag.value] = cls
        else:
            raise TypeError(f'{tag} of {cls} must be an Enum')

    def decoder(value):
        if not isinstance(value, Mapping):
            raise TypeError(f'Unexpected value {repr(value)} for tagged union field: {dataclasses}')
        val_tag = value[tag]
        return tagged_classes[val_tag].from_dict(value)
    return decoder


def union_field(*dataclasses, **kwargs):
    return field(metadata=config(decoder=decode_tagged_union(*dataclasses, **kwargs)))
