from schematics import Model
from schematics.types.compound import ModelType, ListType, DictType
from schematics.types import StringType, BaseType, IntType

from .types import ReferMatchEvent


class ComplyAdvantageMatchField(Model):
    name = StringType()
    tag = StringType(default=None)
    value = StringType()

    def is_dob(self):
        return self.tag == "date_of_birth"

    class Options:
        serialize_when_none = False


class ComplyAdvantageMatchTypeDetails(Model):
    type = StringType(default=None)

    def is_aka(self):
        return self.type == 'aka'


class ComplyAdvantageMatchData(Model):
    id = StringType(required=True)
    name = StringType(required=True)
    ca_fields = ListType(ModelType(ComplyAdvantageMatchField), serialized_name="fields")

    def to_events(self, extra_fields):
        birth_dates = set(field.value for field in self.ca_fields if field.is_dob())

        result = ReferMatchEvent().import_data({
            "match_id": self.id,
            "match_name": self.name,
            "provider_name": "Comply Advantage",
            "match_dates": list(birth_dates),
            **extra_fields
        })
        return [result]


class ComplyAdvantageMatch(Model):
    doc = ModelType(ComplyAdvantageMatchData, required=True)
    match_types_details = DictType(ModelType(ComplyAdvantageMatchTypeDetails), default={})

    def to_events(self):
        aliases = set(k for k, v in self.match_types_details.items() if v.is_aka())
        return self.doc.to_events({
            'aliases': aliases
        })


class ComplyAdvantageResponseData(Model):
    hits = ListType(ModelType(ComplyAdvantageMatch))

    def to_events(self):
        events = []

        for hit in self.hits:
            events = events + hit.to_events()
        return events

    def has_more_hits(self):
        return self.total_hits > self.next_offset

    @property
    def next_offset(self):
        return self.offset + self.limit


class ComplyAdvantageResponseContent(Model):
    data = ModelType(ComplyAdvantageResponseData, required=True)


class ComplyAdvantageResponse(Model):
    message = StringType()
    errors = DictType(BaseType, default={})  # Any json
    content = ModelType(ComplyAdvantageResponseContent, default=None)

    @classmethod
    def from_json(cls, data):
        model = cls().import_data(data, apply_defaults=True)
        model.validate()
        return model

    def to_validated_events(self):
        if self.content is None:
            return []
        events = self.content.data.to_events()
        return [e.as_validated_json() for e in events]
