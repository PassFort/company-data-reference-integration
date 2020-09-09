from collections.abc import Iterable, Sequence, Mapping

from schematics.types import (
    ListType,
)


class MaybeListType(ListType):
    def _coerce(self, value):
        if isinstance(value, list):
            return value
        elif isinstance(value, (str, Mapping)):  # unacceptable iterables
            pass
        elif isinstance(value, Sequence):
            return value
        elif isinstance(value, Iterable):
            return value
        return [value]
