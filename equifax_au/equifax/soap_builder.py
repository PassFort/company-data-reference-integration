from lxml import etree
from lxml.builder import ElementMaker

from collections import namedtuple

class EnvelopeBuilder():
    def __init__(self, namespaces):

        ns_def = namedtuple('namespaces', namespaces.keys())

        ns_dict = {}
        for name, url in namespaces.items():
            ns_dict[name] = ElementMaker(namespace=url)

        self.ns = ns_def(**ns_dict)
        self.soap = ElementMaker(namespace=namespaces['soapenv'], nsmap=namespaces)

    def build_security(self, username, password):
        security = self.ns.wsse.Security(
            self.ns.wsse.UsernameToken(
                self.ns.wsse.Username(username),
                self.ns.wsse.Password(password),
            )
        )
        return security

    def build_consents(self):
        idm_consents = self.ns.idm.consents()
        list_of_consents = [
            'AEC-ER',
            'MIRUS-HER',
            'BDMBC',
            'BDMMC',
            'BDMCON',
            'CITIZEN-DOC',
            'DIAC-RBD',
            'VEDA-CBCOMM',
            'VEDA-CBCONS',
            'VEDA-CBPR',
            'DL',
            'ACC-PEPS',
            'ACC-COMPLINK',
            'IMMICARD-DOC',
            'MEDICARE-CARD',
            'VEDA-NTD',
            'DFAT-AP',
            'DIAC-VEVO',
            'POAC',
            'MIRUS-SPD',
            'VEDA-PND',
            'VEDA-EVVELOCITY',
            'VEDA-SFD',
            'IMG-DOC',
            'SFA',
            'PNV',
            'DVI',
        ]

        for consent_code in list_of_consents:
            idm_consents.append(
                self.ns.idm.consent(consent_code, {'status': '1'})
            )
        return idm_consents


    def print(self, request_xml):
        return etree.tostring(request_xml, encoding='unicode' , xml_declaration=False, pretty_print=True)

    