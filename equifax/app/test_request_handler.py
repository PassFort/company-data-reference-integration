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
            actual,
            {
                'errors': [
                    {
                        "code": ErrorCode.MISCONFIGURATION_ERROR.value,
                        "message": "Invalid member number and/or security code",
                        "source": "PROVIDER"
                    }
                ]
            })

    def test_process_additional_info(self):
        actual = process_equifax_response(with_additional_info)
        self.assertEqual(
            actual,
            {
                'errors': [
                    {
                        "code": ErrorCode.PROVIDER_UNKNOWN_ERROR.value,
                        "message": "Invalid xml formatted input - missing xml tag (CustomerInfo)",
                        "source": "PROVIDER"
                    }
                ]
            }
        )

    def test_process_multiple_errors(self):
        actual = process_equifax_response(bad_province_and_city)
        self.assertEqual(
            actual,
            {
                'errors': [
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
            }
        )

    def test_process_successful_response(self):
        actual = process_equifax_response(success_response)
        self.assertEqual(actual, {'errors': []})
