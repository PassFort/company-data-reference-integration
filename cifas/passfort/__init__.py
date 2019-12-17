from typing import List
from enum import Enum
from collections.abc import Mapping
from dataclasses import field, is_dataclass
from dataclasses_json import config


class EntityType(Enum):
    INDIVIDUAL = 'INDIVIDUAL'
    COMPANY = 'COMPANY'


def decode_tagged_union(*dataclasses: List[type], tag: str = 'type', unknown_type: type = None):
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
        val_class = tagged_classes.get(val_tag, unknown_type)

        if not val_class:
            raise TypeError(f'Invalid tag: {tag}')

        if is_dataclass(val_class):
            return val_class.from_dict(value, infer_missing=True)
        return val_class(value)

    return decoder


def union_field(*dataclasses, **kwargs):
    return field(metadata=config(decoder=decode_tagged_union(*dataclasses, **kwargs)))


def union_list(*dataclasses, **kwargs):
    decoder = decode_tagged_union(*dataclasses, **kwargs) 
    return field(
        metadata=config(
            decoder=lambda value: [
                decoder(item) for item in value
            ],
        ),
    )
