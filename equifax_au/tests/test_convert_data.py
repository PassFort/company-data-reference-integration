import pytest
from collections import OrderedDict

from equifax.convert_data import xml_to_dict_response

def test_convert_xml_to_dict(client):
    response_xml = '''<soapenv:Envelope>
        <soapenv:Header></soapenv:Header>
        <soapenv:Body>
            <request p1="Property 01">
                obs_test
            </request>
        </soapenv:Body>
    </soapenv:Envelope>
    '''
    response_dict = xml_to_dict_response(response_xml)

    assert response_dict == OrderedDict([
                                ("request", OrderedDict([
                                    ("@p1", "Property 01"),
                                    ("#text", "obs_test")])
                                )])
