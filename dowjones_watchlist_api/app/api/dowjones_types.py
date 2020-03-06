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


class PersonRecord(XmlElementModel):
    tag_name = 'person'
    peid = XmlAttribute(XmlStringType())
    date = XmlAttribute(XmlStringType())

    gender = XmlChildContent(XmlStringType())
    deceased = XmlChildContent(XmlBoolType(bool_values=['true', 'false']))
    name_details = XmlChild(PersonNameDetails)


class DataResults(XmlElementModel):
    tag_name = 'records'
    person = XmlChild(PersonRecord)
