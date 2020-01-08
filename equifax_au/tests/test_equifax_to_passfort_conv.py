import pytest
from equifax.convert_data import equifax_to_passfort_data


BASE_EQUIFAX_DATA = '''<?xml version="1.0" encoding="UTF-8"?>
<soapenv:Envelope
    xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/"
    xmlns:vh="http://vedaxml.com/soap/header/v-header-v1-8.xsd"
    xmlns:wsa="http://www.w3.org/2005/08/addressing"
    xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
    xmlns:ns5="http://vedaxml.com/vxml2/idmatrix-v4-0.xsd">
    <soapenv:Body>
        <ns5:response>
            {}
            <ns5:component-responses>
                <ns5:verification-response>
                    <ns5:search-results>
                        {}
                    </ns5:search-results>
                </ns5:verification-response>
            </ns5:component-responses>
        </ns5:response>
    </soapenv:Body>
</soapenv:Envelope>'''

ACCEPT = '''<ns5:response-outcome>
                <ns5:overall-outcome>ACCEPT</ns5:overall-outcome>
            </ns5:response-outcome>'''

REJECT = '''<ns5:response-outcome>
                <ns5:overall-outcome>REJECT</ns5:overall-outcome>
            </ns5:response-outcome>'''

BASE_EQUIFAX_DATA_ERROR = '''<?xml version="1.0" encoding="UTF-8"?>
<soapenv:Envelope
    xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/">
    <soapenv:Body>{}</soapenv:Body>
</soapenv:Envelope>'''

def test_empty_package(client):
    response_body = equifax_to_passfort_data('<soapenv:Envelope><soapenv:Header></soapenv:Header><soapenv:Body></soapenv:Body></soapenv:Envelope>')

    assert response_body == {
                                "output_data": {
                                    'decision': 'ERROR'
                                },
                                "raw": '<soapenv:Envelope><soapenv:Header></soapenv:Header><soapenv:Body></soapenv:Body></soapenv:Envelope>',
                                "errors": []
                            }

def test_record_with_one_datasource_without_match(client):
    equifax_data = BASE_EQUIFAX_DATA.format(REJECT
        , '''<ns5:search-result
                 match-indicator="FAIL"
                 match-score="0"
                 search-name="VEDA-CBCOMM-0051">
             </ns5:search-result>''')

    response_body = equifax_to_passfort_data(equifax_data)

    assert response_body == {
                                "output_data": {
                                    'decision': 'FAIL',
                                    'entity_type': 'INDIVIDUAL',
                                    'electronic_id_check': {
                                        'matches': [
                                            {
                                                'database_name': 'Credit Bureau Commercial (v3)',
                                                'database_type': 'CREDIT',
                                                'matched_fields': [],
                                                'count': 0,
                                            }
                                        ]
                                    }
                                },
                                "raw": equifax_data,
                                "errors": []
                            }
#['TIMEOUT', 'REJECT_ON_EXCLUSION', 'ERROR']:
def test_record_with_one_datasource_without_match_timeout(client):
    equifax_data = BASE_EQUIFAX_DATA.format(
        '''<ns5:response-outcome>
               <ns5:overall-outcome>TIMEOUT</ns5:overall-outcome>
           </ns5:response-outcome>''', '')

    response_body = equifax_to_passfort_data(equifax_data)

    assert response_body == {
                                "output_data": {
                                    'decision': 'ERROR'
                                },
                                "raw": equifax_data,
        "errors": [{'code': 403, 'message': 'Provider Error: TIMEOUT'}]
                            }

def test_record_with_one_datasource_without_match_error(client):
    equifax_data = BASE_EQUIFAX_DATA.format(
        '''<ns5:response-outcome>
               <ns5:overall-outcome>ERROR</ns5:overall-outcome>
           </ns5:response-outcome>''', '')

    response_body = equifax_to_passfort_data(equifax_data)

    assert response_body == {
                                "output_data": {
                                    'decision': 'ERROR'
                                },
                                "raw": equifax_data,
        "errors": [{'code': 303, 'message': 'Provider Error: UNKNOWN ERROR'}]
                            }

def test_record_with_one_datasource_without_match_rejection(client):
    reject_on_exclusion = '''<ns5:response-outcome>
                                <ns5:overall-outcome>REJECT_ON_EXCLUSION</ns5:overall-outcome>
                            </ns5:response-outcome>'''

    equifax_data = BASE_EQUIFAX_DATA.format(reject_on_exclusion
        , '''<ns5:search-result
                 match-indicator="FAIL"
                 match-score="0"
                 search-name="VEDA-CBCOMM-0051">
             </ns5:search-result>''')

    response_body = equifax_to_passfort_data(equifax_data)

    assert response_body == {
                                "output_data": {
                                    'decision': 'FAIL',
                                    'entity_type': 'INDIVIDUAL',
                                    'electronic_id_check': {
                                        'matches': [
                                            {
                                                'database_name': 'Credit Bureau Commercial (v3)',
                                                'database_type': 'CREDIT',
                                                'matched_fields': [],
                                                'count': 0,
                                            }
                                        ]
                                    }
                                },
                                "raw": equifax_data,
                                "errors": []
                            }

def test_record_with_one_datasource_with_surname_match(client):
    equifax_data = BASE_EQUIFAX_DATA.format(ACCEPT, '''
        <ns5:search-result match-indicator="PASS" match-score="87" search-name="VEDA-CBCOMM-0051">
            <ns5:individual-name match-score="100" match-score-weight="12">
                <ns5:family-name match-indicator="Surname" match-score="100" match-score-weight="4" search-value="SPDSNVUB"/>
                <ns5:first-given-name match-indicator="First_Name" match-score="0" match-score-weight="4" search-value="SPDDFNFJQ"/>
                <ns5:other-given-name match-indicator="Middle_Names" match-score="0" match-score-weight="4" search-value="SPDMNNVH"/>
            </ns5:individual-name>
        </ns5:search-result>''')

    response_body = equifax_to_passfort_data(equifax_data)

    assert response_body == {
                                "output_data": {
                                    'decision': 'PASS',
                                    'entity_type': 'INDIVIDUAL',
                                    'electronic_id_check': {
                                        'matches': [
                                            {
                                                'database_name': 'Credit Bureau Commercial (v3)',
                                                'database_type': 'CREDIT',
                                                'matched_fields': ['SURNAME'],
                                                'count': 1
                                            }
                                        ]
                                    }
                                },
                                "raw": equifax_data,
                                "errors": []
                            }


def test_record_with_one_datasource_with_forename_match(client):
    equifax_data = BASE_EQUIFAX_DATA.format(ACCEPT, '''
        <ns5:search-result match-indicator="PASS" match-score="87" search-name="VEDA-CBCOMM-0051">
            <ns5:individual-name match-score="100" match-score-weight="12">
                <ns5:family-name match-indicator="Surname" match-score="0" match-score-weight="4" search-value="SPDSNVUB"/>
                <ns5:first-given-name match-indicator="First_Name" match-score="100" match-score-weight="4" search-value="SPDDFNFJQ"/>
                <ns5:other-given-name match-indicator="Middle_Names" match-score="0" match-score-weight="4" search-value="SPDMNNVH"/>
            </ns5:individual-name>
        </ns5:search-result>''')

    response_body = equifax_to_passfort_data(equifax_data)

    assert response_body == {
                                "output_data": {
                                    'decision': 'PASS',
                                    'entity_type': 'INDIVIDUAL',
                                    'electronic_id_check': {
                                        'matches': [
                                            {
                                                'database_name': 'Credit Bureau Commercial (v3)',
                                                'database_type': 'CREDIT',
                                                'matched_fields': ['FORENAME'],
                                                'count': 1
                                            }
                                        ]
                                    }
                                },
                                "raw": equifax_data,
                                "errors": []
                            }


def test_record_with_one_datasource_with_dob_complete_match(client):
    equifax_data = BASE_EQUIFAX_DATA.format(ACCEPT, '''
        <ns5:search-result match-indicator="PASS" match-score="87" search-name="VEDA-CBCOMM-0051">
            <ns5:date-of-birth match-indicator="Date" match-score="100" match-score-weight="10" search-value="1980-11-13"/>
        </ns5:search-result>''')

    response_body = equifax_to_passfort_data(equifax_data)
    assert response_body == {
                                "output_data": {
                                    'decision': 'PASS',
                                    'entity_type': 'INDIVIDUAL',
                                    'electronic_id_check': {
                                        'matches': [
                                            {
                                                'database_name': 'Credit Bureau Commercial (v3)',
                                                'database_type': 'CREDIT',
                                                'matched_fields': ['DOB'],
                                                'count': 1
                                            }
                                        ]
                                    }
                                },
                                "raw": equifax_data,
                                "errors": []
                            }

def test_record_with_one_datasource_with_address_match(client):
    equifax_data = BASE_EQUIFAX_DATA.format(ACCEPT, '''
        <ns5:search-result match-indicator="PASS" match-score="87" search-name="VEDA-CBCOMM-0051">
            <ns5:current-address match-score="100" match-score-weight="20">
                <ns5:unit-number match-indicator="Unit_Number_Noalpha" match-score="100" match-score-weight="4" search-value="79"/>
                <ns5:street-number match-indicator="Street_Number_Noalpha" match-score="100" match-score-weight="4" search-value="4"/>
                <ns5:street-name match-indicator="Address_Part1" match-score="100" match-score-weight="4" search-value="HYAM"/>
                <ns5:suburb match-indicator="Address_Part2" match-score="100" match-score-weight="4" search-value="BALMAIN"/>
                <ns5:state match-indicator="State" match-score="100" match-score-weight="4" search-value="NSW"/>
                <ns5:postcode match-indicator="Postal_Area" match-score="100" match-score-weight="4" search-value="2041"/>
            </ns5:current-address>
        </ns5:search-result>''')

    response_body = equifax_to_passfort_data(equifax_data)

    assert response_body == {
                                "output_data": {
                                    'decision': 'PASS',
                                    'entity_type': 'INDIVIDUAL',
                                    'electronic_id_check': {
                                        'matches': [
                                            {
                                                'database_name': 'Credit Bureau Commercial (v3)',
                                                'database_type': 'CREDIT',
                                                'matched_fields': ['ADDRESS'],
                                                'count': 1
                                            }
                                        ]
                                    }
                                },
                                "raw": equifax_data,
                                "errors": []
                            }

def test_record_with_one_datasource_with_previous_address_match(client):
    equifax_data = BASE_EQUIFAX_DATA.format(ACCEPT, '''
        <ns5:search-result match-indicator="PASS" match-score="87" search-name="VEDA-CBCOMM-0051">
            <ns5:current-address match-score="0" match-score-weight="0">
                <ns5:unit-number match-indicator="Unit_Number_Noalpha" match-score="0" match-score-weight="0" search-value="79"/>
                <ns5:street-number match-indicator="Street_Number_Noalpha" match-score="0" match-score-weight="0" search-value="4"/>
                <ns5:street-name match-indicator="Address_Part1" match-score="0" match-score-weight="0" search-value="HYAM"/>
                <ns5:suburb match-indicator="Address_Part2" match-score="0" match-score-weight="0" search-value="BALMAIN"/>
                <ns5:state match-indicator="State" match-score="0" match-score-weight="0" search-value="NSW"/>
                <ns5:postcode match-indicator="Postal_Area" match-score="0" match-score-weight="0" search-value="2041"/>
            </ns5:current-address>
            <ns5:previous-address match-score="100" match-score-weight="20">
                <ns5:unit-number match-indicator="Unit_Number_Noalpha" match-score="100" match-score-weight="4" search-value="79"/>
                <ns5:street-number match-indicator="Street_Number_Noalpha" match-score="100" match-score-weight="4" search-value="4"/>
                <ns5:street-name match-indicator="Address_Part1" match-score="100" match-score-weight="4" search-value="HYAM"/>
                <ns5:suburb match-indicator="Address_Part2" match-score="100" match-score-weight="4" search-value="BALMAIN"/>
                <ns5:state match-indicator="State" match-score="100" match-score-weight="4" search-value="NSW"/>
                <ns5:postcode match-indicator="Postal_Area" match-score="100" match-score-weight="4" search-value="2041"/>
            </ns5:previous-address>
        </ns5:search-result>''')

    response_body = equifax_to_passfort_data(equifax_data)

    assert response_body == {
                                "output_data": {
                                    'decision': 'PASS',
                                    'entity_type': 'INDIVIDUAL',
                                    'electronic_id_check': {
                                        'matches': [
                                            {
                                                'database_name': 'Credit Bureau Commercial (v3)',
                                                'database_type': 'CREDIT',
                                                'matched_fields': ['ADDRESS'],
                                                'count': 1
                                            }
                                        ]
                                    }
                                },
                                "raw": equifax_data,
                                "errors": []
                            }

def test_record_with_one_datasource_with_address_match_full_fields(client):
    equifax_data = BASE_EQUIFAX_DATA.format(ACCEPT, '''
        <ns5:search-result match-indicator="PASS" match-score="87" search-name="VEDA-CBCOMM-0051">
            <ns5:current-address match-score="100" match-score-weight="24">
                <ns5:property match-indicator="Property" match-score="100" match-score-weight="4" search-value="property test"/>
                <ns5:unit-number match-indicator="Unit_Number_Noalpha" match-score="100" match-score-weight="4" search-value="79"/>
                <ns5:street-number match-indicator="Street_Number_Noalpha" match-score="100" match-score-weight="4" search-value="4"/>
                <ns5:street-name match-indicator="Address_Part1" match-score="100" match-score-weight="4" search-value="HYAM"/>
                <ns5:suburb match-indicator="Address_Part2" match-score="100" match-score-weight="4" search-value="BALMAIN"/>
                <ns5:state match-indicator="State" match-score="100" match-score-weight="4" search-value="NSW"/>
                <ns5:postcode match-indicator="Postal_Area" match-score="100" match-score-weight="4" search-value="2041"/>
                <ns5:country match-indicator="Country" match-score="100" match-score-weight="4" search-value="AU"/>
            </ns5:current-address>
        </ns5:search-result>''')

    response_body = equifax_to_passfort_data(equifax_data)

    assert response_body == {
                                "output_data": {
                                    'decision': 'PASS',
                                    'entity_type': 'INDIVIDUAL',
                                    'electronic_id_check': {
                                        'matches': [
                                            {
                                                'database_name': 'Credit Bureau Commercial (v3)',
                                                'database_type': 'CREDIT',
                                                'matched_fields': ['ADDRESS'],
                                                'count': 1
                                            }
                                        ]
                                    }
                                },
                                "raw": equifax_data,
                                "errors": []
                            }

def test_record_with_one_datasource_with_address_match_honouring_match_score(client):
    equifax_data = BASE_EQUIFAX_DATA.format(ACCEPT, '''
        <ns5:search-result match-indicator="PASS" match-score="87" search-name="VEDA-CBCOMM-0051">
            <ns5:individual-name match-score="100" match-score-weight="12">
                <ns5:family-name match-indicator="Surname" match-score="0" match-score-weight="4" search-value="SPDSNVUB"/>
                <ns5:first-given-name match-indicator="First_Name" match-score="100" match-score-weight="4" search-value="SPDDFNFJQ"/>
                <ns5:other-given-name match-indicator="Middle_Names" match-score="0" match-score-weight="4" search-value="SPDMNNVH"/>
            </ns5:individual-name>
            <ns5:current-address match-score="100" match-score-weight="20">
                <ns5:unit-number match-indicator="Unit_Number_Noalpha" match-score="100" match-score-weight="4" search-value="79"/>
                <ns5:street-number match-indicator="Street_Number_Noalpha" match-score="100" match-score-weight="4" search-value="4"/>
                <ns5:street-name match-indicator="Address_Part1" match-score="0" match-score-weight="4" search-value="HYAM"/>
                <ns5:suburb match-indicator="Address_Part2" match-score="100" match-score-weight="4" search-value="BALMAIN"/>
                <ns5:state match-indicator="State" match-score="100" match-score-weight="4" search-value="NSW"/>
                <ns5:postcode match-indicator="Postal_Area" match-score="0" match-score-weight="4" search-value="2041"/>
            </ns5:current-address>
        </ns5:search-result>''')

    response_body = equifax_to_passfort_data(equifax_data)

    assert response_body == {
                                "output_data": {
                                    'decision': 'PASS',
                                    'entity_type': 'INDIVIDUAL',
                                    'electronic_id_check': {
                                        'matches': [
                                            {
                                                'database_name': 'Credit Bureau Commercial (v3)',
                                                'database_type': 'CREDIT',
                                                'matched_fields': ['FORENAME', 'ADDRESS'],
                                                'count': 1
                                            }
                                        ]
                                    }
                                },
                                "raw": equifax_data,
                                "errors": []
                            }
def test_record_with_one_datasource_with_database_type_credit(client):
    equifax_data = BASE_EQUIFAX_DATA.format(ACCEPT, '''
        <ns5:search-result match-indicator="PASS" match-score="87" search-name="VEDA-CBCOMM-0051">
            <ns5:individual-name match-score="100" match-score-weight="12">
                <ns5:family-name match-indicator="Surname" match-score="100" match-score-weight="4" search-value="SPDSNVUB"/>
                <ns5:first-given-name match-indicator="First_Name" match-score="0" match-score-weight="4" search-value="SPDDFNFJQ"/>
                <ns5:other-given-name match-indicator="Middle_Names" match-score="0" match-score-weight="4" search-value="SPDMNNVH"/>
            </ns5:individual-name>
        </ns5:search-result>''')

    response_body = equifax_to_passfort_data(equifax_data)

    assert response_body == {
                                "output_data": {
                                    'decision': 'PASS',
                                    'entity_type': 'INDIVIDUAL',
                                    'electronic_id_check': {
                                        'matches': [
                                            {
                                                'database_name': 'Credit Bureau Commercial (v3)',
                                                'database_type': 'CREDIT',
                                                'matched_fields': ['SURNAME'],
                                                'count': 1
                                            }
                                        ]
                                    }
                                },
                                "raw": equifax_data,
                                "errors": []
                            }

def test_record_with_one_datasource_with_database_type_civil(client):
    equifax_data = BASE_EQUIFAX_DATA.format(ACCEPT, '''
        <ns5:search-result match-indicator="PASS" match-score="87" search-name="ACT-DL-0072">
            <ns5:individual-name match-score="100" match-score-weight="12">
                <ns5:family-name match-indicator="Surname" match-score="100" match-score-weight="4" search-value="SPDSNVUB"/>
                <ns5:first-given-name match-indicator="First_Name" match-score="0" match-score-weight="4" search-value="SPDDFNFJQ"/>
                <ns5:other-given-name match-indicator="Middle_Names" match-score="0" match-score-weight="4" search-value="SPDMNNVH"/>
            </ns5:individual-name>
        </ns5:search-result>''')

    response_body = equifax_to_passfort_data(equifax_data)

    assert response_body == {
                                "output_data": {
                                    'decision': 'PASS',
                                    'entity_type': 'INDIVIDUAL',
                                    'electronic_id_check': {
                                        'matches': [
                                            {
                                                'database_name': 'Drivers Licence - ACT (DVS)',
                                                'database_type': 'CIVIL',
                                                'matched_fields': ['SURNAME'],
                                                'count': 1
                                            }
                                        ]
                                    }
                                },
                                "raw": equifax_data,
                                "errors": []
                            }

def test_record_with_two_datasource_with_diff_database_type(client):
    equifax_data = BASE_EQUIFAX_DATA.format(ACCEPT, '''
        <ns5:search-result match-indicator="PASS" match-score="87" search-name="VEDA-CBCOMM-0051">
            <ns5:individual-name match-score="100" match-score-weight="12">
                <ns5:family-name match-indicator="Surname" match-score="100" match-score-weight="4" search-value="SPDSNVUB"/>
                <ns5:first-given-name match-indicator="First_Name" match-score="0" match-score-weight="4" search-value="SPDDFNFJQ"/>
                <ns5:other-given-name match-indicator="Middle_Names" match-score="0" match-score-weight="4" search-value="SPDMNNVH"/>
            </ns5:individual-name>
        </ns5:search-result>
        <ns5:search-result match-indicator="PASS" match-score="87" search-name="ACT-DL-0072">
            <ns5:individual-name match-score="100" match-score-weight="12">
                <ns5:family-name match-indicator="Surname" match-score="100" match-score-weight="4" search-value="SPDSNVUB"/>
                <ns5:first-given-name match-indicator="First_Name" match-score="0" match-score-weight="4" search-value="SPDDFNFJQ"/>
                <ns5:other-given-name match-indicator="Middle_Names" match-score="0" match-score-weight="4" search-value="SPDMNNVH"/>
            </ns5:individual-name>
        </ns5:search-result>''')

    response_body = equifax_to_passfort_data(equifax_data)

    assert response_body == {
                                "output_data": {
                                    'decision': 'PASS',
                                    'entity_type': 'INDIVIDUAL',
                                    'electronic_id_check': {
                                        'matches': [
                                            {
                                                'database_name': 'Credit Bureau Commercial (v3)',
                                                'database_type': 'CREDIT',
                                                'matched_fields': ['SURNAME'],
                                                'count': 1
                                            },
                                            {
                                                'database_name': 'Drivers Licence - ACT (DVS)',
                                                'database_type': 'CIVIL',
                                                'matched_fields': ['SURNAME'],
                                                'count': 1
                                            }
                                        ]
                                    }
                                },
                                "raw": equifax_data,
                                "errors": []
                            }

def test_record_error_bad_request(client):
    equifax_data = BASE_EQUIFAX_DATA_ERROR.format('''
        <soapenv:Fault>
            <faultcode>soapenv:Server</faultcode>
            <faultstring>Policy Falsified</faultstring>
            <faultactor>http://vedaxml.com/sys2/idmatrix-v*</faultactor>
            <detail>
                <l7:policyResult status="Bad Request" xmlns:l7="http://www.layer7tech.com/ws/policy/fault"/>
            </detail>
        </soapenv:Fault>''')

    response_body = equifax_to_passfort_data(equifax_data)
    assert response_body == {
                                "output_data": {
                                    'decision': 'ERROR'
                                },
                                "raw": equifax_data,
                                "errors": [{'code': 201, 'message': 'Provider Error: Bad Request'}]
                            }

def test_record_error_auth_error(client):
    equifax_data = BASE_EQUIFAX_DATA_ERROR.format('''
        <soapenv:Fault>
            <faultcode>soapenv:Server</faultcode>
            <faultstring>Policy Falsified</faultstring>
            <faultactor>http://vedaxml.com/sys2/idmatrix-v*</faultactor>
            <detail>
                <l7:policyResult status="Authentication Failed" xmlns:l7="http://www.layer7tech.com/ws/policy/fault"/>
            </detail>
        </soapenv:Fault>''')

    response_body = equifax_to_passfort_data(equifax_data)
    assert response_body == {
                                "output_data": {
                                    'decision': 'ERROR'
                                },
                                "raw": equifax_data,
                                "errors": [{'code': 205, 'message': 'Provider Error: Authentication Failed'}]
                            }

def test_record_error_service_not_found(client):
    equifax_data = BASE_EQUIFAX_DATA_ERROR.format('''
        <soapenv:Fault>
            <faultcode>soapenv:Server</faultcode>
            <faultstring>Policy Falsified</faultstring>
            <faultactor>http://vedaxml.com/sys2/idmatrix-v*</faultactor>
            <detail>
                <l7:policyResult status="Service Not Found. The request may have been sent to an invalid URL, or intended for an unsupported operation."
                xmlns:l7="http://www.layer7tech.com/ws/policy/fault"/>
            </detail>
        </soapenv:Fault>''')

    response_body = equifax_to_passfort_data(equifax_data)
    assert response_body == {
                                "output_data": {
                                    'decision': 'ERROR'
                                },
                                "raw": equifax_data,
                                "errors": [{'code': 205, 'message': 'Provider Error: Service Not Found. The request may have been sent to an invalid URL, or intended for an unsupported operation.'}]
                            }

def test_record_error_application_fault(client):
    equifax_data = BASE_EQUIFAX_DATA_ERROR.format('''
        <soapenv:Fault>
            <faultcode>soapenv:Server</faultcode>
            <faultstring>Policy Falsified</faultstring>
            <faultactor>http://vedaxml.com/sys2/idmatrix-v*</faultactor>
            <detail>
                <l7:policyResult status="Error in Assertion Processing"
                xmlns:l7="http://www.layer7tech.com/ws/policy/fault"/>
            </detail>
        </soapenv:Fault>''')

    response_body = equifax_to_passfort_data(equifax_data)
    assert response_body == {
                                "output_data": {
                                    'decision': 'ERROR'
                                },
                                "raw": equifax_data,
                                "errors": [{'code': 303, 'message': 'Provider Error: Error in Assertion Processing'}]
                            }

def test_record_error_config_issue(client):
    equifax_data = BASE_EQUIFAX_DATA_ERROR.format('''
        <soapenv:Fault>
            <faultcode>soapenv:Server</faultcode>
            <faultstring>An error occurred when processing idMatixOperation</faultstring>
        </soapenv:Fault>''')

    response_body = equifax_to_passfort_data(equifax_data)
    assert response_body == {
                                "output_data": {
                                    'decision': 'ERROR'
                                },
                                "raw": equifax_data,
                                "errors": [{'code': 303, 'message': 'Provider Error: An error occurred when processing idMatixOperation'}]
                            }

def test_record_error_server_error(client):
    equifax_data = BASE_EQUIFAX_DATA_ERROR.format('''
        <soapenv:Fault>
            <faultcode>soapenv:Server</faultcode>
            <faultstring>Policy Falsified</faultstring>
            <faultactor>http://vedaxml.com/sys2/idmatrix-v*</faultactor>
            <detail>
            <l7:policyResult status="Service Temporarily Unavailable "
            xmlns:l7="http://www.layer7tech.com/ws/policy/fault"/>
            </detail>
        </soapenv:Fault>''')

    response_body = equifax_to_passfort_data(equifax_data)
    assert response_body == {
                                "output_data": {
                                    'decision': 'ERROR'
                                },
                                "raw": equifax_data,
                                "errors": [{'code': 302, 'message': 'Provider Error: Service Temporarily Unavailable'}]
                            }
