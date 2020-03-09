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
    first_name = XmlChildContent(XmlStringType(), serialized_name='first-name')
    surname = XmlChildContent(XmlStringType())


class PersonNames(XmlElementModel):
    tag_name = 'person-names'
    values = XmlChildren(PersonNameValue)


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


class PersonRecord(XmlElementModel):
    tag_name = 'person'
    peid = XmlAttribute(XmlStringType())
    date = XmlAttribute(XmlStringType())

    gender = XmlChildContent(XmlStringType(), default=None)
    deceased = XmlChildContent(XmlBoolType(bool_values=['true', 'false']))
    name_details = XmlChild(PersonNameDetails)
    country_details = XmlChild(CountryDetails)


class DataResults(XmlElementModel):
    tag_name = 'records'
    person = XmlChild(PersonRecord)
