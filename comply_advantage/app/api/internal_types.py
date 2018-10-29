from schematics import Model
from schematics.types.compound import ModelType, ListType, DictType
from schematics.types import StringType, BaseType, IntType, UTCDateTimeType, UnionType

from typing import List, TYPE_CHECKING

from .types import ReferMatchEvent, PepMatchEvent, SanctionsMatchEvent, SanctionData, AdverseMediaMatchEvent, \
    MediaArticle, ComplyAdvantageConfig

if TYPE_CHECKING:
    from .types import MatchEvent


class ComplyAdvantageException(Exception):
    pass


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


class ComplyAdvantageSourceNote(Model):
    name = StringType(default=None)
    url = StringType(default=None)
    aml_types = ListType(StringType, default=[])
    country_codes = ListType(StringType)
    listing_started_utc = UTCDateTimeType()
    listing_ended_utc = UTCDateTimeType(default=None)

    def is_sanction(self):
        return len(self.aml_types) and "sanction" in self.aml_types

    def as_sanction_data(self):
        return SanctionData({
            "type": "sanction",
            "list": self.name,
            "is_current": self.listing_ended_utc is None
        })


class ComplyAdvantageMediaData(Model):
    url = StringType(default=None)
    pdf_url = StringType(default=None)
    title = StringType(default=None)
    snippet = StringType(default=None)
    date = UTCDateTimeType(default=None)

    def as_media_article(self):
        return MediaArticle({
            'url': self.url,
            'pdf_url': self.pdf_url,
            'title': self.title,
            'snippet': self.snippet,
            'date': self.date and self.date.date()
        })


class ComplyAdvantageMatchData(Model):
    id = StringType(required=True)
    name = StringType(required=True)
    ca_fields = ListType(ModelType(ComplyAdvantageMatchField), serialized_name="fields")
    types = ListType(StringType)
    source_notes = DictType(ModelType(ComplyAdvantageSourceNote))
    media = ListType(ModelType(ComplyAdvantageMediaData))

    def to_events(self, extra_fields: dict, config: ComplyAdvantageConfig) -> List['MatchEvent']:
        events = []
        birth_dates = set(field.value for field in self.ca_fields if field.is_dob())

        is_pep = "pep" in self.types
        is_sanction = "sanction" in self.types
        has_adverse_media = "adverse-media" in self.types

        base_data = {
            "match_id": self.id,
            "match_name": self.name,
            "provider_name": "Comply Advantage",
            "match_dates": list(birth_dates),
            **extra_fields
        }

        if is_pep:
            pep_result = PepMatchEvent().import_data({
                "pep": {"match": True, "tier": self.get_pep_tier()},
                **base_data
            })
            events.append(pep_result)
        if is_sanction:
            sanction_result = SanctionsMatchEvent().import_data({
                "sanctions": self.get_sanctions(),
                **base_data
            })
            events.append(sanction_result)
        if config.include_adverse_media and has_adverse_media:
            adverse_media_result = AdverseMediaMatchEvent().import_data({
                "media": [m.as_media_article() for m in self.media],
                **base_data
            })
            events.append(adverse_media_result)

        if len(events) == 0:
            events.append(ReferMatchEvent().import_data(base_data))
        return events

    def get_sanctions(self):
        return [note.as_sanction_data() for name, note in self.source_notes.items() if note.is_sanction()]

    def get_pep_tier(self):
        all_pep_types = sorted([t for t in self.types if t.startswith("pep-")])
        if len(all_pep_types):
            return int(all_pep_types[0].replace("pep-class-", ""))
        return None


class ComplyAdvantageMatch(Model):
    doc = ModelType(ComplyAdvantageMatchData, required=True)
    # comply advantage returns empty list if no details are present.
    match_types_details = UnionType(
        (
            DictType(ModelType(ComplyAdvantageMatchTypeDetails), default={}),
            ListType
        ), field=BaseType)

    def to_events(self, config: ComplyAdvantageConfig):
        if self.match_types_details:
            aliases = set(k for k, v in self.match_types_details.items() if v.is_aka())
        else:
            aliases = set()
        return self.doc.to_events(
            {
                'aliases': aliases
            },
            config)


class ComplyAdvantageResponseData(Model):
    hits = ListType(ModelType(ComplyAdvantageMatch), default=[])
    total_hits = IntType(default=0)
    offset = IntType(default=0)
    limit = IntType(default=0)
    search_id = IntType(required=True, serialized_name="id")

    def to_events(self, config: ComplyAdvantageConfig):
        events = []

        for hit in self.hits:
            events = events + hit.to_events(config)
        return events

    def has_more_hits(self):
        return self.offset + self.limit < self.total_hits


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

    def to_validated_events(self, config: ComplyAdvantageConfig):
        if self.content is None:
            return []
        events = self.content.data.to_events(config)
        return [e.as_validated_json() for e in events]

    def has_more_pages(self):
        if self.content is None:
            return False
        return self.content.data.has_more_hits()

    @property
    def search_id(self):
        if self.content is None:
            return None
        return self.content.data.search_id
