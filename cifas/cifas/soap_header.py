from zeep import xsd


fh = '{http://header.find-cifas.org.uk}'
StandardHeader = xsd.Element(
    f'{fh}StandardHeader',
    xsd.ComplexType([
        xsd.Element(f'{fh}RequestingInstitution', xsd.Integer()),
        xsd.Element(f'{fh}OwningMemberNumber', xsd.Integer()),
        xsd.Element(f'{fh}ManagingMemberNumber', xsd.Integer()),
        xsd.Element(f'{fh}CurrentUser', xsd.String()),
        xsd.Element(f'{fh}SchemaVersion', xsd.String()),
    ])
)
