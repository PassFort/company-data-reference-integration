from copy import deepcopy
import re
from schematics.exceptions import ValidationError, ConversionError
from schematics.models import Model
from schematics.types import ModelType, ListType, StringType, UnionType

from .types import ErrorCode, MatchField, DatabaseType


class XMLTagBaseType(ModelType):
    def convert(self, value, context=None):

        if isinstance(value, dict):
            to_convert = value
        elif isinstance(value, str):
            to_convert = {
                '#text': value
            }
        else:
            return value
        return super().convert(to_convert, context)


class OneOrMoreType(ListType):

    def convert(self, value, context=None):
        if isinstance(value, list):
            to_convert = value
        else:
            to_convert = [value]
        return super().convert(to_convert, context)


def to_snake_case(input):
    return re.sub('(?!^)([A-Z]+)', r'_\1', input).lower()


class EquifaxErrorDetails(Model):
    error_code = StringType(serialized_name='ErrorCode', default=None)
    source_code = StringType(serialized_name='SourceCode', default=None)
    additional_information = StringType(serialized_name='AdditionalInformation', default=None)
    description = StringType(serialized_name='Description', required=True)

    def as_passfort_error(self):
        internal_error_code = ErrorCode.MISCONFIGURATION_ERROR.value if self.error_code == 'E0819' \
            else ErrorCode.PROVIDER_UNKNOWN_ERROR.value
        message = f'{self.description}'
        if self.additional_information:
            message = f'{message} ({self.additional_information})'

        return {
            'code': internal_error_code,
            'source': 'PROVIDER',
            'message': message
        }


class EquifaxError(Model):
    errors = OneOrMoreType(ModelType(EquifaxErrorDetails), serialized_name='Error', default=None)

    def as_passfort_errors(self):
        return [e.as_passfort_error() for e in self.errors]


class EquifaxErrorReport(Model):
    main = ModelType(EquifaxError, serialized_name='Errors', default=None)


class EquifaxItem(Model):
    name = StringType(serialized_name='@name', default=None)
    value = StringType(serialized_name='@value', default=None)
    text = StringType(serialized_name='#text', default=None)


class TradeItem(Model):
    '''
    Every trade item returned is a qualifying trade (will match a requirement)
    '''
    items = ListType(ModelType(EquifaxItem), default=[], serialized_name='CSItem')

    def get_item(self, name):
        return next((i for i in self.items if i.name == name), None)

    def item_content(self, name):
        item = self.get_item(name)
        if item is not None:
            return item.text
        return None

    def is_true(self, name):
        item = self.get_item(name)
        return item is not None and item.text == 'Y'

    @property
    def database_name(self):
        return self.item_content('FamilyName') or self.item_content('InstitutionName') or 'Credit',

    @property
    def matched_requirement(self):
        if self.is_true('NameAndDOBMatch'):
            matched_required_fields = [MatchField.FORENAME.value, MatchField.SURNAME.value, MatchField.DOB.value]
        elif self.is_true('NameAndAddressMatch'):
            matched_required_fields = [MatchField.FORENAME.value, MatchField.SURNAME.value, MatchField.ADDRESS.value]
        else:
            raise NotImplementedError('Qualifying trade should match on DOB or address')
        return {
            'database_name': self.database_name,
            'matched_fields': matched_required_fields,
            'count': 1
        }

    @property
    def match_data(self):
        matched_fields = []

        if self.is_true('LastNameMatch'):
            matched_fields.append(MatchField.SURNAME.value)
        if self.is_true('FirstNameMatch'):
            matched_fields.append(MatchField.FORENAME.value)
        if self.is_true('DateOfBirthMatch'):
            matched_fields.append(MatchField.DOB.value)
        if all(
                self.is_true(f)
                for f in [
                    'AddressCivicMatch',
                    'AddressStreetNameMatch',
                    'AddressCityMatch',
                    'AddressPostalCodeMatch',
                    'AddressProvinceMatch'
                ]
        ):
            matched_fields.append(MatchField.ADDRESS.value)

        extra_fields = [
            {
                'name': to_snake_case(field),
                'value': self.item_content(field)
            } for field in ['MemberNumber', 'AccountNumber', 'DateOpened', 'DateLastReported', 'InstitutionName']
        ]

        return {
            'database_name': self.database_name,
            'database_type': DatabaseType.CREDIT.value,
            'matched_fields': matched_fields,
            'extra': extra_fields
        }


class Trades(EquifaxItem):
    trades = OneOrMoreType(ModelType(TradeItem), serialized_name='CSItem', default=[])

    @property
    def matches(self):
        return [t.match_data for t in self.trades]

    @property
    def satisfied_requirements(self):
        return [t.matched_requirement for t in self.trades]


class HeaderType(ModelType):

    def convert(self, value, context=None):
        if isinstance(value, HeaderItem):
            return value
        if isinstance(value, dict) and value['@name'] == 'SubProductType' and value['@value'] == 'Header':
            return super().convert(value, context)
        else:
            raise ConversionError(f'The value must be a header: {value}')


class DualSourceType(ModelType):

    def convert(self, value, context=None):
        if isinstance(value, DualSourceItem):
            return value
        if isinstance(value, dict) and value['@name'] == 'SubProductType' and value['@value'] == 'Dual':
            return super().convert(value, context)
        else:
            raise ConversionError(f'The value must be a dual section: {value}')


class HeaderItem(EquifaxItem):
    name = StringType(serialized_name='@name', required=True, choices=['SubProductType'])
    value = StringType(serialized_name='@value', required=True, choices=['Header'])
    items = OneOrMoreType(ModelType(EquifaxItem), serialized_name='CSItem', required=True)

    def is_dual_source_verified(self):
        dual_source_hit = next((item.text for item in self.items if item.name == 'DualSourceHit'), None)
        decision = next((item.text for item in self.items if item.name == 'DualSourceDecision'), None)

        return dual_source_hit == 'Y' and decision == 'Y'


class DualSourceItem(EquifaxItem):
    name = StringType(serialized_name='@name', required=True, choices=['SubProductType'])
    value = StringType(serialized_name='@value', required=True, choices=['Dual'])
    trades = ModelType(Trades, serialized_name='CSItem', required=True)

    @property
    def matches(self):
        return self.trades.matches

    @property
    def satisfied_requirements(self):
        return self.trades.satisfied_requirements


class EquifaxSection(Model):
    main_item = UnionType((HeaderType(HeaderItem), ModelType(DualSourceItem)), required=True, serialized_name='CSItem')


class EquifaxProduct(Model):
    items = OneOrMoreType(ModelType(EquifaxItem), required=True, serialized_name='CSItem')
    sections = OneOrMoreType(ModelType(EquifaxSection), default=[], serialized_name='CSSection')

    rules = [
        {
            'name': 'A name and address match plus a name and DOB match',
            'active': False,
            'database_types': [DatabaseType.CREDIT.value],
            'distinct_sources': True,
            'requires': [
                {
                    'matched_fields': [MatchField.FORENAME.value, MatchField.SURNAME.value, MatchField.ADDRESS.value],
                    'count': 1
                },
                {
                    'matched_fields': [MatchField.FORENAME.value, MatchField.SURNAME.value, MatchField.DOB.value],
                    'count': 1
                },
            ],
            'result': '2+2'
        },
        {
            'name': 'A name and address match',
            'active': False,
            'database_types': [DatabaseType.CREDIT.value],
            'distinct_sources': True,
            'requires': [
                {
                    'matched_fields': [MatchField.FORENAME.value, MatchField.SURNAME.value, MatchField.ADDRESS.value],
                    'count': 1
                }
            ],
            'result': '1+1'
        },
        {
            'name': 'A name and DOB match',
            'active': False,
            'database_types': [DatabaseType.CREDIT.value],
            'distinct_sources': True,
            'requires': [
                {
                    'matched_fields': [MatchField.FORENAME.value, MatchField.SURNAME.value, MatchField.DOB.value],
                    'count': 1
                }
            ],
            'result': '1+1'
        },
        {
            'name': 'No address or DOB match',
            'database_types': [DatabaseType.CREDIT.value],
            'distinct_sources': True,
            'active': False,
            'requires': [],
            'result': 'Fail'
        }
    ]

    def validate_items(self, data, value):
        if any(item.text == 'AML' and item.name == 'ProductType' for item in value):
            return value
        raise ValidationError(f'Expected to receive AML Product. Received: {value}')

    def validate_sections(self, data, value):
        if len([section for section in value if isinstance(section.main_item, HeaderItem)]) == 1:
            return value
        raise ValidationError(f'Expected to receive AML Product Header. Received: {value}')

    @property
    def header(self):
        return next(s.main_item for s in self.sections if isinstance(s.main_item, HeaderItem))

    @property
    def dual_section(self):
        return next((s.main_item for s in self.sections if isinstance(s.main_item, DualSourceItem)), None)

    def matched_rule(self, rules, satisfied_requirements):
        satisfied_req_set = set(frozenset(r['matched_fields']) for r in satisfied_requirements)

        for rule in rules:
            requirements = rule.get('requires', [])
            if len(requirements) == len(satisfied_requirements):
                req_set = set(frozenset(r['matched_fields']) for r in requirements)

                if req_set == satisfied_req_set:
                    return rule
        return rules[-1]

    def as_ekyc_result(self):
        matches = []
        satisfied_requirements = []
        rules = deepcopy(self.rules)
        if self.dual_section is not None:
            matches = self.dual_section.matches
            satisfied_requirements = self.dual_section.satisfied_requirements

        if self.header.is_dual_source_verified():
            assert len(matches) > 1 and len(satisfied_requirements) == 2

        matched_rule = self.matched_rule(rules, satisfied_requirements)
        matched_rule['active'] = True
        matched_rule['satisfied_by'] = satisfied_requirements
        return {
            'matches': matches,
            'rules': rules
        }


class EquifaxCoreServices(Model):
    product = ModelType(EquifaxProduct, serialized_name='CSProduct')


class CodeItem(Model):
    code = StringType(required=True, serialized_name='@code')
    description = StringType(default=None, serialized_name='@description')


class FileOwner(Model):
    bureau_code = XMLTagBaseType(EquifaxItem, required=True, serialized_name='BureauCode')
    bureau_contact = XMLTagBaseType(EquifaxItem, default=None, serialized_name='BureauContactInformation')

    @property
    def name(self):
        return self.bureau_contact.text if self.bureau_contact is not None else self.bureau_code.text


class CreditFile(Model):
    unique_number = XMLTagBaseType(EquifaxItem, default={}, serialized_name='UniqueNumber')
    file_since_date = XMLTagBaseType(EquifaxItem, default={}, serialized_name='FileSinceDate')
    date_of_last_activity = XMLTagBaseType(EquifaxItem, default={}, serialized_name='DateOfLastActivity')
    date_of_request = XMLTagBaseType(EquifaxItem, default={}, serialized_name='DateOfRequest')
    file_owner = ModelType(FileOwner, default=None, serialized_name='FileOwner')
    hit_code = ModelType(CodeItem, serialized_name='HitCode', required=True)
    hit_strength_indicator = ModelType(CodeItem, serialized_name='HitStrengthIndicator')

    def as_credit_file_match(self):
        extra_fields = [
            {
                'name': attr_name,
                'value': getattr(self, attr_name).text
            }
            for attr_name in [
                'file_since_date',
                'date_of_last_activity',
                'date_of_request'
            ]
        ] + [
            {
                'name': 'bureau_code',
                'value': self.file_owner.bureau_code.text if self.file_owner else None
            },
            {
                'name': 'hit_code_value',
                'value': self.hit_code.code
            },
            {
                'name': 'hit_code_description',
                'value': self.hit_code.description
            },
            {
                'name': 'hit_strength_value',
                'value': self.hit_strength_indicator.code if self.hit_strength_indicator else None
            },
            {
                'name': 'hit_code_description',
                'value': self.hit_strength_indicator.description if self.hit_strength_indicator else None
            }
        ]
        return {
            'unique_number': self.unique_number.text,
            'bureau_name': self.file_owner.name if self.file_owner else 'Equifax',
            'extra': extra_fields
        }


class EquifaxConsumerReportHeader(Model):
    credit_files = OneOrMoreType(ModelType(CreditFile), serialized_name='CreditFile', default=[])

    def credit_file_matches(self):
        return [credit_file.as_credit_file_match() for credit_file in self.credit_files]


class EquifaxConsumerReport(Model):
    efx_core_svc = ModelType(EquifaxCoreServices, serialized_name='CNEquifaxCoreServices', required=True)
    header = ModelType(EquifaxConsumerReportHeader, serialized_name='CNHeader', required=True)

    def as_ekyc_result(self):
        core_result = self.efx_core_svc.product.as_ekyc_result()
        return {
            **core_result,
            'credit_files': self.header.credit_file_matches()
        }


class EquifaxConsumerReports(Model):
    efx_consumer_report = ModelType(EquifaxConsumerReport, serialized_name='CNConsumerCreditReport')


class EquifaxReport(Model):
    efx_consumer_reports = ModelType(EquifaxConsumerReports, serialized_name='CNConsumerCreditReports', default=None)
    request_number = StringType(required=True, serialized_name='@requestNumber')

    def get_ekyc_result(self):
        if self.efx_consumer_reports:
            consumer_report = self.efx_consumer_reports.efx_consumer_report.as_ekyc_result()
            return {
                'electronic_id_check': {
                    **consumer_report,
                    'provider_reference_number': self.request_number
                }
            }
        return None


class EquifaxResponse(Model):
    error_report = ModelType(EquifaxErrorReport, serialized_name='CNErrorReport', default=None)
    efx_report = ModelType(EquifaxReport, serialized_name='EfxReport', default=None)

    def get_errors(self):
        if self.error_report and self.error_report.main and self.error_report.main.errors:
            return self.error_report.main.as_passfort_errors()
        return []


class EquifaxResponseWithRoot(Model):
    root = ModelType(EquifaxResponse, serialized_name='EfxTransmit', default=None)

    @classmethod
    def from_json(cls, data):
        model = cls().import_data(data, apply_defaults=True)
        model.validate()
        return model

    def get_errors(self):
        return self.root.get_errors()

    def get_ekyc_result(self):
        if self.root.efx_report:
            return self.root.efx_report.get_ekyc_result()
        return None

