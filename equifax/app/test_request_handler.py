import unittest

from .request_handler import process_equifax_response
from .api.types import ErrorCode

bad_security_code = '<?xml version="1.0" encoding="UTF-8" ?>' \
                    '<EfxTransmit xmlns="http://www.equifax.ca/XMLSchemas/EfxToCust" ' \
                    'xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" ' \
                    'xsi:schemaLocation="http://www.equifax.ca/XMLSchemas/EfxToCust ' \
                    'http://www.equifax.ca/XMLSchemas/Production/CNEfxTransmitToCust.xsd" >' \
                    '<CNErrorReport><SegmentId>SERXM</SegmentId>' \
                    '<VersionNumber>010</VersionNumber><CustomerCode>R147</CustomerCode>' \
                    '<CustomerNumber></CustomerNumber><TransactionReferenceNumber>' \
                    '</TransactionReferenceNumber>' \
                    '<Errors>' \
                    '<Error>' \
                    '<SourceCode>IQID</SourceCode><ErrorCode>E0819</ErrorCode>' \
                    '<Description>Invalid member number and/or security code</Description>' \
                    '</Error>' \
                    '</Errors></CNErrorReport></EfxTransmit>'

with_additional_info = '<?xml version="1.0" encoding="UTF-8" ?>' \
                       '<EfxTransmit xmlns="http://www.equifax.ca/XMLSchemas/EfxToCust" ' \
                       'xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" ' \
                       'xsi:schemaLocation="http://www.equifax.ca/XMLSchemas/EfxToCust ' \
                       'http://www.equifax.ca/XMLSchemas/UAT/CNEfxTransmitToCust.xsd" >' \
                       '<CNErrorReport><SegmentId>SERXM</SegmentId><VersionNumber>010</VersionNumber>' \
                       '<CustomerCode></CustomerCode><CustomerNumber>' \
                       '</CustomerNumber><TransactionReferenceNumber></TransactionReferenceNumber>' \
                       '<Errors>' \
                       '<Error><SourceCode>SPK00</SourceCode><ErrorCode>E0807</ErrorCode>' \
                       '<AdditionalInformation>CustomerInfo</AdditionalInformation>' \
                       '<Description>Invalid xml formatted input - missing xml tag' \
                       '</Description>' \
                       '</Error>' \
                       '</Errors></CNErrorReport></EfxTransmit>'

success_response = '<?xml version="1.0" encoding="UTF-8" ?>' \
                   '<EfxTransmit xmlns="http://www.equifax.ca/XMLSchemas/EfxToCust" ' \
                   'xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" ' \
                   'xsi:schemaLocation="http://www.equifax.ca/XMLSchemas/EfxToCust ' \
                   'http://www.equifax.ca/XMLSchemas/UAT/CNEfxTransmitToCust.xsd" >' \
                   '<EfxReport requestNumber="1" reportId="CNSIGNONACKNOWLEDGEMENT">' \
                   '<CNSignonAcknowledgement signonStatus=\'OK\' /></EfxReport></EfxTransmit>'


bad_province_and_city = '<?xml version="1.0" encoding="UTF-8" ?>' \
                        '<EfxTransmit xmlns="http://www.equifax.ca/XMLSchemas/EfxToCust" ' \
                        'xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" ' \
                        'xsi:schemaLocation="http://www.equifax.ca/XMLSchemas/EfxToCust ' \
                        'http://www.equifax.ca/XMLSchemas/UAT/CNEfxTransmitToCust.xsd" >' \
                        '<CNErrorReport>' \
                        '<SegmentId>SERXM</SegmentId>' \
                        '<VersionNumber>010</VersionNumber>' \
                        '<CustomerCode>R147</CustomerCode>' \
                        '<CustomerNumber>999FX00333</CustomerNumber><TransactionReferenceNumber>' \
                        '</TransactionReferenceNumber>' \
                        '<Errors>' \
                        '<Error>' \
                        '<SourceCode>SAC00</SourceCode>' \
                        '<ErrorCode>EV304</ErrorCode>' \
                        '<Description>Invalid city name</Description>' \
                        '</Error>' \
                        '<Error>' \
                        '<SourceCode>SAC00</SourceCode>' \
                        '<ErrorCode>EV305</ErrorCode>' \
                        '<Description>Invalid province code</Description>' \
                        '</Error>' \
                        '</Errors></CNErrorReport></EfxTransmit>'


class TestErrorProcessing(unittest.TestCase):
    def test_expose_bad_configuration(self):
        actual = process_equifax_response(bad_security_code)
        self.assertEqual(
            actual['errors'],
            [
                {
                    "code": ErrorCode.MISCONFIGURATION_ERROR.value,
                    "message": "Invalid member number and/or security code",
                    "source": "PROVIDER"
                }
            ]
        )

    def test_process_additional_info(self):
        actual = process_equifax_response(with_additional_info)
        self.assertEqual(
            actual['errors'],
            [
                {
                    "code": ErrorCode.PROVIDER_UNKNOWN_ERROR.value,
                    "message": "Invalid xml formatted input - missing xml tag (CustomerInfo)",
                    "source": "PROVIDER"
                }
            ]
        )

    def test_process_multiple_errors(self):
        actual = process_equifax_response(bad_province_and_city)
        self.assertEqual(
            actual['errors'],
            [
                {
                    "code": ErrorCode.PROVIDER_UNKNOWN_ERROR.value,
                    "message": "Invalid city name",
                    "source": "PROVIDER"
                },
                {
                    "code": ErrorCode.PROVIDER_UNKNOWN_ERROR.value,
                    "message": "Invalid province code",
                    "source": "PROVIDER"
                }
            ]
        )

    def test_process_successful_response_signon(self):
        actual = process_equifax_response(success_response)
        self.assertEqual(actual['errors'], [])


class TestUnexpectedXml(unittest.TestCase):

    def test_extra_elements(self):
        two_errors_with_extra_elem = '<?xml version="1.0" encoding="UTF-8" ?>' \
                                     '<EfxTransmit xmlns="http://www.equifax.ca/XMLSchemas/EfxToCust" ' \
                                     'xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" ' \
                                     'xsi:schemaLocation="http://www.equifax.ca/XMLSchemas/EfxToCust ' \
                                     'http://www.equifax.ca/XMLSchemas/UAT/CNEfxTransmitToCust.xsd" >' \
                                     '  <CNErrorReport>' \
                                     '    <SegmentId>SERXM</SegmentId>' \
                                     '    <VersionNumber>010</VersionNumber>' \
                                     '    <CustomerCode>R147</CustomerCode>' \
                                     '    <CustomerNumber>999FX00333</CustomerNumber><TransactionReferenceNumber>' \
                                     '    </TransactionReferenceNumber>' \
                                     '    <Errors>' \
                                     '      <Error>' \
                                     '        <SourceCode>SAC00</SourceCode>' \
                                     '        <ErrorCode>EV304</ErrorCode>' \
                                     '        <Description>Invalid city name</Description>' \
                                     '      </Error>' \
                                     '      <Extra>TEST_TEXT_HERE</Extra>' \
                                     '      <Error>' \
                                     '        <SourceCode>SAC00</SourceCode>' \
                                     '        <ErrorCode>EV305</ErrorCode>' \
                                     '        <Description>Invalid province code</Description>' \
                                     '      </Error>' \
                                     '    </Errors>' \
                                     '  </CNErrorReport>' \
                                     '</EfxTransmit>'

        actual = process_equifax_response(two_errors_with_extra_elem)
        self.assertEqual(len(actual['errors']), 2)
        error_list = actual['raw']['EfxTransmit']['CNErrorReport']['Errors']['Error']
        self.assertEqual(len(error_list), 2)
        extra_element = actual['raw']['EfxTransmit']['CNErrorReport']['Errors']['Extra']
        self.assertEqual(extra_element, 'TEST_TEXT_HERE')

    def test_extra_elements(self):
        two_errors_with_extra_name = '<?xml version="1.0" encoding="UTF-8" ?>' \
                                     '<EfxTransmit xmlns="http://www.equifax.ca/XMLSchemas/EfxToCust" ' \
                                     'xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" ' \
                                     'xsi:schemaLocation="http://www.equifax.ca/XMLSchemas/EfxToCust ' \
                                     'http://www.equifax.ca/XMLSchemas/UAT/CNEfxTransmitToCust.xsd" >' \
                                     '  <CNErrorReport>' \
                                     '    <SegmentId>SERXM</SegmentId>' \
                                     '    <VersionNumber>010</VersionNumber>' \
                                     '    <CustomerCode>R147</CustomerCode>' \
                                     '    <CustomerNumber>999FX00333</CustomerNumber><TransactionReferenceNumber>' \
                                     '    </TransactionReferenceNumber>' \
                                     '    <Errors name=\'TEST_NAME_HERE\'>' \
                                     '      <Error>' \
                                     '        <SourceCode>SAC00</SourceCode>' \
                                     '        <ErrorCode>EV304</ErrorCode>' \
                                     '        <Description>Invalid city name</Description>' \
                                     '      </Error>' \
                                     '      <Error>' \
                                     '        <SourceCode>SAC00</SourceCode>' \
                                     '        <ErrorCode>EV305</ErrorCode>' \
                                     '        <Description>Invalid province code</Description>' \
                                     '      </Error>' \
                                     '    </Errors>' \
                                     '  </CNErrorReport>' \
                                     '</EfxTransmit>'

        actual = process_equifax_response(two_errors_with_extra_name)
        self.assertEqual(len(actual['errors']), 2)
        error_list = actual['raw']['EfxTransmit']['CNErrorReport']['Errors']['Error']
        self.assertEqual(len(error_list), 2)
        extra_element = actual['raw']['EfxTransmit']['CNErrorReport']['Errors']['@name']
        self.assertEqual(extra_element, 'TEST_NAME_HERE')


class TestResultProcessing(unittest.TestCase):

    def get_and_assert_active_rule(self, rules, expected_active_index):
        for index, rule in enumerate(rules):
            if index == expected_active_index:
                self.assertTrue(rule['active'])
            else:
                self.assertFalse(rule['active'])
        return rules[expected_active_index]

    def test_process_successful_response_2_plus_2(self):
        with open('mock_data/2_plus_2.xml', 'rb') as f:
            test_input = f.read()
        actual = process_equifax_response(test_input)
        self.assertEqual(actual['errors'], [])

        matches = actual['output_data']['electronic_id_check']['matches']
        self.assertEqual(len(matches), 2)

        self.assertEqual(
            sorted(matches[0]['matched_fields']),
            ['ADDRESS', 'DOB', 'FORENAME', 'SURNAME']
        )

        rules = actual['output_data']['electronic_id_check']['rules']

        active_rule = self.get_and_assert_active_rule(rules, 0)
        self.assertEqual(active_rule['result'], '2+2')
        self.assertEqual(len(active_rule['satisfied_by']), 2)

    def test_process_1_plus_1_address(self):
        with open('mock_data/1_plus_1_address.xml', 'rb') as f:
                test_input = f.read()
        actual = process_equifax_response(test_input)
        self.assertEqual(actual['errors'], [])

        matches = actual['output_data']['electronic_id_check']['matches']
        self.assertEqual(len(matches), 1)

        self.assertEqual(
            sorted(matches[0]['matched_fields']),
            ['ADDRESS', 'FORENAME', 'SURNAME']
        )

        rules = actual['output_data']['electronic_id_check']['rules']

        active_rule = self.get_and_assert_active_rule(rules, 1)
        self.assertEqual(active_rule['result'], '1+1')
        self.assertEqual(len(active_rule['satisfied_by']), 1)
        self.assertEqual(
            sorted(active_rule['satisfied_by'][0]['matched_fields']),
            ['ADDRESS', 'FORENAME', 'SURNAME'])

    def test_process_1_plus_1_dob(self):
        with open('mock_data/1_plus_1_dob.xml', 'rb') as f:
            test_input = f.read()
        actual = process_equifax_response(test_input)
        self.assertEqual(actual['errors'], [])

        matches = actual['output_data']['electronic_id_check']['matches']
        self.assertEqual(len(matches), 1)

        self.assertEqual(
            sorted(matches[0]['matched_fields']),
            ['ADDRESS', 'DOB', 'FORENAME', 'SURNAME']
        )

        rules = actual['output_data']['electronic_id_check']['rules']

        active_rule = self.get_and_assert_active_rule(rules, 2)
        self.assertEqual(active_rule['result'], '1+1')
        self.assertEqual(len(active_rule['satisfied_by']), 1)
        self.assertEqual(
            sorted(active_rule['satisfied_by'][0]['matched_fields']),
            ['DOB', 'FORENAME', 'SURNAME'])

    def test_process_fail_no_trade(self):
        with open('mock_data/fail_no_trade.xml', 'rb') as f:
            test_input = f.read()
        actual = process_equifax_response(test_input)
        self.assertEqual(actual['errors'], [])

        matches = actual['output_data']['electronic_id_check']['matches']
        self.assertEqual(len(matches), 0)

        rules = actual['output_data']['electronic_id_check']['rules']

        active_rule = self.get_and_assert_active_rule(rules, 3)
        self.assertEqual(active_rule['result'], 'Fail')
        self.assertEqual(len(active_rule['satisfied_by']), 0)


class TestRecordKeeping(unittest.TestCase):
    def test_surfaces_record_keeping_fields(self):
        with open('mock_data/2_plus_2.xml', 'rb') as f:
            test_input = f.read()
        actual = process_equifax_response(test_input)
        self.assertEqual(actual['errors'], [])

        self.assertEqual(actual['output_data']['electronic_id_check']['provider_reference_number'], '1')

        credit_file_data = actual['output_data']['electronic_id_check']['credit_files']

        self.assertEqual(len(credit_file_data), 1)
        self.assertEqual(credit_file_data[0]['unique_number'], '0050165588')
        self.assertEqual(credit_file_data[0]['bureau_name'], 'Equifax inc.')

        self.assertListEqual(
            credit_file_data[0]['extra'],
            [
                {'name': 'file_since_date', 'value': '2010-01-01'},
                {'name': 'date_of_last_activity', 'value': '2019-01-04'},
                {'name': 'date_of_request', 'value': '2019-02-05'},
                {'name': 'bureau_code', 'value': '065'},
                {'name': 'hit_code_value', 'value': '1'},
                {'name': 'hit_code_description', 'value': 'HIT'},
                {'name': 'hit_strength_value', 'value': '11'},
                {'name': 'hit_code_description', 'value': 'Regular hit'}
            ]
        )

        matches = actual['output_data']['electronic_id_check']['matches']
        self.assertEqual(len(matches), 2)

        self.assertListEqual(
            matches[0]['extra'],
            [
                {'name': 'member_number', 'value': '650ON42725'},
                {'name': 'account_number', 'value': '123456789044423'},
                {'name': 'date_opened', 'value': '20161003'},
                {'name': 'date_last_reported', 'value': '20190129'},
                {'name': 'institution_name', 'value': 'TD CREDIT CARDS'}
            ]
        )

        self.assertListEqual(
            matches[1]['extra'],
            [
                {'name': 'member_number', 'value': '650BB31015'},
                {'name': 'account_number', 'value': '123456789033323'},
                {'name': 'date_opened', 'value': '20161003'},
                {'name': 'date_last_reported', 'value': '20190129'},
                {'name': 'institution_name', 'value': 'SIMPLII FI CIBC'}
            ]
        )
