from typing import List, Union

from schematics_xmlelem.attributes import XmlAttribute
from schematics_xmlelem.children import (
    XmlChildContent,
    XmlChildrenContent,
    XmlChild,
    XmlNestedChildList,
    XmlChildren
)
from schematics_xmlelem.content import XmlContent
from schematics_xmlelem.model import XmlElementModel
from schematics_xmlelem.types import (
    XmlEnumType,
    XmlStringType,
    XmlIntType,
    XmlBoolType,
    XmlFloatType,
)


def partial_date_string(maybe_year, maybe_month, maybe_day):
    from datetime import date
    if maybe_year is not None and maybe_month is not None and maybe_day is not None:
        return date(maybe_year, maybe_month, maybe_day).strftime('%Y-%m-%d')
    elif maybe_year is not None and maybe_month is not None:
        return date(maybe_year, maybe_month, 1).strftime('%Y-%m')
    elif maybe_year is not None:
        return date(maybe_year, 1, 1).strftime('%Y')
    else:
        return None


class RiskIcon(XmlElementModel):
    tag_name = 'risk-icon'
    kind = XmlChildContent(XmlStringType())


class RiskIcons(XmlElementModel):
    tag_name = 'risk-icons'
    icons = XmlChildrenContent(XmlStringType(), serialized_name='risk-icon')


class SearchResultPayload(XmlElementModel):
    tag_name = 'payload'
    risk_icons = XmlChild(RiskIcons)
    matched_name = XmlChildContent(XmlStringType(), serialized_name='matched-name')


class SearchResultsMatch(XmlElementModel):
    tag_name = 'match'
    peid = XmlAttribute(XmlStringType())
    score = XmlChildContent(XmlFloatType())
    payload = XmlChild(SearchResultPayload)


class SearchResultsBody(XmlElementModel):
    tag_name = 'body'
    matches = XmlChildren(SearchResultsMatch)


class SearchResults(XmlElementModel):
    tag_name = 'search-results'
    body = XmlChild(SearchResultsBody)


class PersonNameValue(XmlElementModel):
    tag_name = 'person-name-value'
    type_ = XmlAttribute(XmlStringType(), serialized_name='name-type', default=None)

    first_name = XmlChildContent(XmlStringType(), serialized_name='first-name')
    middle_name = XmlChildContent(XmlStringType(), serialized_name='middle-name', default=None)
    surname = XmlChildContent(XmlStringType())

    def join(self):
        return ' '.join(name for name in [
            self.first_name,
            self.middle_name,
            self.surname,
        ] if name is not None)


class PersonNames(XmlElementModel):
    tag_name = 'person-names'
    name = XmlChild(PersonNameValue)


class PersonNameDetails(XmlElementModel):
    tag_name = 'person-name-details'
    values = XmlChildren(PersonNames)


class Country(XmlElementModel):
    tag_name = 'country'
    djii_region_code = XmlAttribute(XmlStringType(), serialized_name='djii-region-code')
    iso2_country_code = XmlAttribute(XmlStringType(), serialized_name='iso2-country-code')
    iso3_country_code = XmlAttribute(XmlStringType(), default=None, serialized_name='iso3-country-code')


class CountryValue(XmlElementModel):
    tag_name = 'country-value'
    country_type = XmlAttribute(XmlStringType(), serialized_name='country-type')

    country = XmlChild(Country)


class CountryDetails(XmlElementModel):
    tag_name = 'country-details'
    country_values = XmlChildren(CountryValue)


class Date(XmlElementModel):
    tag_name = 'date'
    day = XmlAttribute(XmlIntType(), default=None)
    month = XmlAttribute(XmlIntType(), default=None)
    year = XmlAttribute(XmlIntType(), default=None)
    type_ = XmlAttribute(XmlStringType(), default=None, serialized_name='date-type')

    def to_partial_date_string(self):
        return partial_date_string(self.year, self.month, self.day)


class DateDetails(XmlElementModel):
    tag_name = 'date-details'
    dates = XmlChildren(Date)


class ActiveStatus(XmlElementModel):
    tag_name = 'active-status'
    is_active = XmlContent(XmlBoolType(bool_values=['Active', 'Inactive']))


class Description(XmlElementModel):
    tag_name = 'description'
    text = XmlAttribute(XmlStringType(), serialized_name='description1')


class XmlElementWithTimePeriodAttributes(XmlElementModel):
    since_day = XmlAttribute(XmlIntType(), serialized_name='since-day', default=None)
    since_month = XmlAttribute(XmlIntType(), serialized_name='since-month', default=None)
    since_year = XmlAttribute(XmlIntType(), serialized_name='since-year', default=None)

    to_day = XmlAttribute(XmlIntType(), serialized_name='to-day', default=None)
    to_month = XmlAttribute(XmlIntType(), serialized_name='to-month', default=None)
    to_year = XmlAttribute(XmlIntType(), serialized_name='to-year', default=None)

    @property
    def since_partial_date(self):
        if self.since_year is None:
            return None
        return partial_date_string(self.since_year, self.since_month, self.since_day)

    @property
    def to_partial_date(self):
        if self.to_year is None:
            return None
        return partial_date_string(self.to_year, self.to_month, self.to_day)


class OccupationTitle(XmlElementWithTimePeriodAttributes):
    tag_name = 'occupation-title'
    category = XmlAttribute(XmlStringType(), serialized_name='occupation-category')
    text = XmlContent(XmlStringType())


class Role(XmlElementModel):
    tag_name = 'role'
    type_ = XmlAttribute(XmlStringType(), serialized_name='role-type')
    title = XmlChild(OccupationTitle)


class Sanction(XmlElementWithTimePeriodAttributes):
    tag_name = 'sanctions-reference'
    list_provider_name = XmlAttribute(XmlStringType(), serialized_name='list-provider-name')
    list_provider_code = XmlAttribute(XmlStringType(), serialized_name='list-provider-code')
    status = XmlAttribute(XmlStringType())

    list_ = XmlContent(XmlStringType())


class Source(XmlElementModel):
    tag_name = 'source'
    reference = XmlContent(XmlStringType())


class WatchlistContent(XmlElementModel):
    tag_name = 'watchlist-content'
    active_status = XmlChild(ActiveStatus)
    descriptions = XmlNestedChildList(Description)
    roles = XmlNestedChildList(Role, serialized_name='role-details')
    sanctions = XmlNestedChildList(Sanction, serialized_name='sanctions-reference-details')
    sources = XmlNestedChildList(Source, serialized_name='source-details')
    profile_notes = XmlChildContent(XmlStringType(), default=None, serialized_name='profile-notes')


class Associate(XmlElementModel):
    tag_name = 'associate'
    peid = XmlAttribute(XmlStringType(), default=None)
    relationship = XmlAttribute(XmlStringType())
    description = XmlAttribute(XmlStringType(), serialized_name='description1')
    ex = XmlAttribute(XmlBoolType(bool_values=['true', 'false']))


class PersonRecord(XmlElementModel):
    tag_name = 'person'
    peid = XmlAttribute(XmlStringType())
    date = XmlAttribute(XmlStringType())

    gender = XmlChildContent(XmlStringType(), default=None)
    deceased = XmlChildContent(XmlBoolType(bool_values=['true', 'false']))
    name_details = XmlChild(PersonNameDetails)
    country_details = XmlChild(CountryDetails)
    date_details = XmlChild(DateDetails, default=None)
    watchlist_content = XmlChild(WatchlistContent)

    associates = XmlNestedChildList(Associate, serialized_name='associates')


class DataResults(XmlElementModel):
    tag_name = 'records'
    person = XmlChild(PersonRecord, default=None)
