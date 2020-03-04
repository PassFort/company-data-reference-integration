from typing import List, Union


from schematics_xmlelem.attributes import XmlAttribute
from schematics_xmlelem.children import XmlChildContent, XmlChild, XmlNestedChildList, XmlChildren
from schematics_xmlelem.content import XmlContent
from schematics_xmlelem.model import XmlElementModel
from schematics_xmlelem.types import XmlEnumType, XmlStringType, XmlIntType, XmlBoolType, XmlFloatType


class SearchResultsMatch(XmlElementModel):
    tag_name = "match"
    peid = XmlAttribute(XmlStringType())


class SearchResultsBody(XmlElementModel):
    tag_name = "body"
    matches = XmlChildren(SearchResultsMatch)


class SearchResults(XmlElementModel):
    tag_name = "search-results"
    body = XmlChild(SearchResultsBody)
