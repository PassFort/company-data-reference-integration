from collections import defaultdict

from schematics import Model
from schematics.types.compound import ModelType, ListType, DictType
from schematics.types import StringType, BaseType, IntType, UTCDateTimeType, UnionType, BooleanType, DecimalType

from simplejson import JSONDecodeError

from typing import List, TYPE_CHECKING

from .types import ReferMatchEvent, PepMatchEvent, SanctionsMatchEvent, SanctionData, AdverseMediaMatchEvent, \
    MediaArticle, ComplyAdvantageConfig, Associate, Detail, Source, TimePeriod

if TYPE_CHECKING:
    from .types import MatchEvent, ScreeningRequestData


class ComplyAdvantageException(Exception):
    pass


class ComplyAdvantageAssociate(Model):
    name = StringType(required=True)

    def as_associate(self):
        return Associate({
            'name': self.name
        })


class ComplyAdvantageMatchField(Model):
    name = StringType(default='Other')
    tag = StringType(default=None)
    value = StringType(required=True)
    source = StringType(default=None)

    def is_dob(self):
        return self.tag == 'date_of_birth'

    def is_dod(self):
        return self.tag == 'date_of_death'

    def is_related_url(self):
        return self.tag == 'related_url'

    def is_detail(self):
        return not self.is_dob() and not self.is_dod() and not self.is_related_url()

    def as_source(self):
        if self.is_related_url():
            return Source({
                'name': self.name,
                'url': self.value,
            })
        return Source({
            'name': self.name,
            'description': self.value
        })

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
    country_codes = ListType(StringType, default=[])
    listing_started_utc = UTCDateTimeType(default=None)
    listing_ended_utc = UTCDateTimeType(default=None)

    def is_sanction(self):
        return len(self.aml_types) and "sanction" in self.aml_types

    def is_current(self):
        return self.listing_ended_utc is None

    def as_sanction_data(self):
        return SanctionData({
            'type': 'sanction',
            'list': self.name,  # Name is actually the list name
            'name': self.url,
            'issuer': ', '.join(set(self.country_codes)),
            'is_current': self.is_current(),
            'time_periods': [
                TimePeriod({
                    'from_date': self.listing_started_utc.date() if self.listing_started_utc else None,
                    'to_date': self.listing_ended_utc.date() if self.listing_ended_utc else None
                })
            ]
        })

    def as_source(self):
        description = None
        if self.listing_ended_utc:
            description = f'Ended on {self.listing_ended_utc.date()}'

        return Source({
            'name': self.name or 'Other',
            'url': self.url,
            'description': description
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
    associates = ListType(ModelType(ComplyAdvantageAssociate), default=[])
    ca_fields = ListType(ModelType(ComplyAdvantageMatchField), serialized_name="fields", default=[])
    types = ListType(StringType)
    source_notes = DictType(ModelType(ComplyAdvantageSourceNote))
    media = ListType(ModelType(ComplyAdvantageMediaData))

    def to_events(self, share_url: StringType, extra_fields: dict, config: ComplyAdvantageConfig) -> List['MatchEvent']:
        events = []
        birth_dates = set(field.value for field in self.ca_fields if field.is_dob())
        death_dates = set(field.value for field in self.ca_fields if field.is_dod())
        sources_from_source_notes = [s.as_source() for k, s in self.source_notes.items() if not s.is_sanction()]
        sources_from_fields = [s.as_source() for s in self.ca_fields if s.is_related_url()]

        is_pep = "pep" in self.types
        is_sanction = "sanction" in self.types
        has_adverse_media = "adverse-media" in self.types

        base_data = {
            "match_id": self.id,
            "match_name": self.name,
            "provider_name": "Comply Advantage",
            "match_dates": list(birth_dates),
            "deceased_dates": list(death_dates),
            "associates": [a.as_associate() for a in self.associates],
            "details": self.get_details(),
            "sources": [self.comply_advantage_entity_source(share_url)] +
            sources_from_source_notes + sources_from_fields,
            **extra_fields
        }

        if len(death_dates) > 0:
            base_data["deceased"] = True

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

    def comply_advantage_entity_source(self, share_url: StringType):
        if share_url:
            url = share_url.replace("search", "entity", 1) + "/" + self.id
            return Source({
                'name': "ComplyAdvantage Entity",
                'url': url,
            })

    def get_sanctions(self):
        return [note.as_sanction_data() for name, note in self.source_notes.items() if note.is_sanction()]

    def get_pep_tier(self):
        all_pep_types = sorted([t for t in self.types if t.startswith("pep-")])
        if len(all_pep_types):
            return int(all_pep_types[0].replace("pep-class-", ""))
        return None

    def get_details(self):
        grouped_detail_fields = defaultdict(set)
        for field in self.ca_fields:
            if field.is_detail():
                grouped_detail_fields[field.name].add(field.value)

        return [Detail({'title': name, 'text': '; '.join(values)}) for name, values in grouped_detail_fields.items()]


class ComplyAdvantageMatch(Model):
    doc = ModelType(ComplyAdvantageMatchData, required=True)
    # comply advantage returns empty list if no details are present.
    match_types_details = UnionType(
        (
            DictType(ModelType(ComplyAdvantageMatchTypeDetails), default={}),
            ListType
        ), field=BaseType)

    def to_events(self, share_url: StringType, config: ComplyAdvantageConfig):
        if self.match_types_details:
            aliases = set(k for k, v in self.match_types_details.items() if v.is_aka())
        else:
            aliases = set()
        return self.doc.to_events(
            share_url,
            {
                'aliases': aliases
            },
            config)


class ComplyAdvantageFilters(Model):
    types = ListType(StringType, required=True)
    fuzziness = DecimalType(required=True)
    birth_year = IntType(default=None)


class ComplyAdvantageResponseData(Model):
    hits = ListType(ModelType(ComplyAdvantageMatch), default=[])
    total_hits = IntType(default=0)
    offset = IntType(default=0)
    limit = IntType(default=0)
    search_id = IntType(required=True, serialized_name="id")

    filters = ModelType(ComplyAdvantageFilters, default={})
    search_term = StringType(default=None)
    share_url = StringType(default=None)

    def to_events(self, config: ComplyAdvantageConfig):
        events = []

        for hit in self.hits:
            events = events + hit.to_events(self.share_url, config)
        return events

    def has_more_hits(self):
        return self.offset + self.limit < self.total_hits


class ComplyAdvantageSearchRequest:

    def __init__(self, search_format):
        self.search_format = search_format

    @classmethod
    def build_request(cls, search_term, fuzziness, type_filter, birth_year=None):
        base_format = {
            "search_term": search_term,
            "fuzziness": fuzziness,
            "filters": {
                "types": type_filter
            },
            "share_url": True,
        }
        if birth_year:
            base_format['filters']['birth_year'] = birth_year
        return cls(base_format)

    @classmethod
    def from_input_data(cls, input_data: 'ScreeningRequestData', config: ComplyAdvantageConfig):
        type_filter = ["pep", "sanction"]

        if config.include_adverse_media:
            type_filter = type_filter + ["adverse-media", "warning", "fitness-probity"]

        birth_year = None
        if input_data.entity_type == 'INDIVIDUAL':
            if input_data.personal_details.dob:
                birth_year = input_data.personal_details.year_from_dob()

        return cls.build_request(input_data.search_term, config.fuzziness, type_filter, birth_year)

    @classmethod
    def from_response_data(cls, response_data: ComplyAdvantageResponseData):
        return cls.build_request(
            response_data.search_term,
            response_data.filters.fuzziness,
            response_data.filters.types,
            response_data.filters.birth_year)

    def paginate(self, offset, limit):
        self.search_format['offset'] = offset
        self.search_format['limit'] = limit
        return self.search_format


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

    @classmethod
    def from_raw(cls, response):
        try:
            raw_response = response.json()
            return raw_response, cls.from_json(raw_response)
        except JSONDecodeError:
            return {}, None

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


class ComplyAdvantageMonitorContent(Model):
    is_monitored = BooleanType(required=True)


class ComplyAdvantageMonitorResponse(Model):
    message = StringType(default="")
    errors = DictType(BaseType, default={})  # Any json
    content = ModelType(ComplyAdvantageMonitorContent, default=None)

    @classmethod
    def from_json(cls, data):
        model = cls().import_data(data, apply_defaults=True)
        model.validate()
        return model

    @property
    def monitor_status(self):
        if self.content is None:
            return None
        return self.content.is_monitored
