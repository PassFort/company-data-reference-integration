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
        from datetime import date
        if self.year is not None and self.month is not None and self.day is not None:
            return date(self.year, self.month, self.day).strftime('%Y-%m-%d')
        elif self.year is not None and self.month is not None:
            return date(self.year, self.month, 1).strftime('%Y-%m')
        elif self.year is not None:
            return date(self.year, 1, 1).strftime('%Y')
        else:
            return None


class DateDetails(XmlElementModel):
    tag_name = 'date-details'
    dates = XmlChildren(Date)


class ActiveStatus(XmlElementModel):
    tag_name = 'active-status'
    is_active = XmlContent(XmlBoolType(bool_values=['Active', 'Inactive']))


class Description(XmlElementModel):
    tag_name = 'description'
    text = XmlAttribute(XmlStringType(), serialized_name='description1')


class WatchlistContent(XmlElementModel):
    tag_name = 'watchlist-content'
    active_status = XmlChild(ActiveStatus)
    descriptions = XmlNestedChildList(Description)


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
    associates = XmlNestedChildList(Associate)


class DataResults(XmlElementModel):
    tag_name = 'records'
    person = XmlChild(PersonRecord, default=None)
