from schematics import Model
from schematics.types import StringType, DateTimeType, ListType, PolyModelType, IntType, BaseType, ModelType


def onfido_credit_source_name(index):
    if index is None:
        return 'Onfido (all credit sources)'
    else:
        return f'Onfido (credit source #{index+1})'


SUPPORTED_IDENTITY_DATABASES = {
    onfido_credit_source_name(None): {
        'AUS', 'AUT', 'BEL', 'FRA', 'DEU', 'IDN', 'IRL', 'ITA', 'LIE', 'MEX', 'NLD', 'PRT', 'PRI', 'RUS', 'SWE', 'CHE',
        'GBR', 'USA'
    },
    'Voting Register': {
        'AFG', 'ALB', 'ARG', 'ARM', 'AUS', 'AZE', 'BLR', 'BEN', 'BGR', 'BDI', 'CMR', 'CAN', 'CYM', 'CHN', 'CRI', 'CUB',
        'EGY', 'EST', 'GEO', 'GRC', 'IND', 'IDN', 'IRN', 'IRL', 'ITA', 'KAZ', 'KEN', 'KGZ', 'LVA', 'LBY', 'LTU', 'MEX',
        'MDA', 'NAM', 'NPL', 'NZL', 'NGA', 'PSE', 'PHL', 'POL', 'PRT', 'ROU', 'SOM', 'ZAF', 'SDN', 'SYR', 'TJK', 'TZA',
        'TTO', 'TUR', 'TKM', 'UGA', 'UKR', 'GBR', 'USA', 'UZB', 'VEN', 'ZWE'
    },
    'Telephone Database': {
        'ALA', 'ALB', 'AND', 'ATG', 'ARM', 'ABW', 'AUS', 'AUT', 'AZE', 'BRB', 'BLR', 'BEL', 'BLZ', 'BEN', 'BMU', 'BTN',
        'BIH', 'BRN', 'BGR', 'BFA', 'KHM', 'CMR', 'CAN', 'CYM', 'CAF', 'CHL', 'COL', 'COG', 'COK', 'CIV', 'HRV', 'CZE',
        'DNK', 'DJI', 'DMA', 'DOM', 'ECU', 'SLV', 'GNQ', 'EST', 'ETH', 'FRO', 'FJI', 'FIN', 'FRA', 'GUF', 'GAB', 'GEO',
        'DEU', 'GIB', 'GRC', 'GRD', 'GLP', 'GTM', 'GIN', 'HND', 'HUN', 'ISL', 'IND', 'IRL', 'ITA', 'JAM', 'JPN', 'JEY',
        'KAZ', 'UNK', 'KGZ', 'LVA', 'LBN', 'LSO', 'LIE', 'LTU', 'LUX', 'MAC', 'MWI', 'MYS', 'MLI', 'MLT', 'MTQ', 'MRT',
        'MYT', 'MEX', 'MDA', 'MCO', 'MSR', 'MAR', 'NLD', 'ANT', 'NZL', 'NIC', 'NER', 'NFK', 'NOR', 'OMN', 'PAK', 'PSE',
        'PAN', 'PRY', 'PER', 'POL', 'PRT', 'PRI', 'QAT', 'REU', 'ROU', 'RUS', 'KNA', 'LCA', 'MAF', 'SPM', 'WSM', 'SAU',
        'SGP', 'SVN', 'ZAF', 'ESP', 'LKA', 'VCT', 'SWE', 'CHE', 'TGO', 'TKM', 'TCA', 'TUV', 'UKR', 'ARE', 'GBR', 'UZB',
        'VUT', 'VEN', 'VGB', 'YUG', 'ZMB'
    },
    'Government': {
        'ARG', 'ARM', 'AUS', 'AZE', 'BRA', 'CAN', 'DNK', 'GEO', 'HKG', 'IRL', 'ISR', 'ITA', 'NZL', 'NOR', 'PRT', 'RUS',
        'SGP', 'ESP', 'SWE', 'TUR', 'UKR', 'USA', 'UZB'
    },
    'Business Registration': {
        'DZA', 'BHR', 'BLR', 'BEL', 'BMU', 'BIH', 'BRN', 'BGR', 'CAN', 'CHL', 'CHN', 'CIV', 'HRV', 'CYP', 'CZE', 'DNK',
        'EGY', 'EST', 'FIN', 'FRA', 'DEU', 'GIB', 'GRC', 'HKG', 'HUN', 'ISL', 'IND', 'IDN', 'IRN', 'ISR', 'KOR', 'KWT',
        'LVA', 'LIE', 'LTU', 'LUX', 'MYS', 'MDA', 'MCO', 'MAR', 'NLD', 'NOR', 'OMN', 'PAK', 'POL', 'PRT', 'QAT', 'ROU',
        'RUS', 'SGP', 'SVK', 'SVN', 'ZAF', 'ESP', 'SWE', 'CHE', 'TWN', 'THA', 'TUN', 'TUR', 'UKR', 'ARE', 'VNM'
    },
    'Consumer Database': {
        'AUS', 'CAN', 'DNK', 'FIN', 'FRA', 'DEU', 'NLD', 'NOR', 'ESP', 'SWE'
    },
    'Utility Registration': {
        'AUS', 'FRA', 'ITA', 'ESP'
    },
    'Postal Authorities': {
        'DNK', 'FIN', 'FRA', 'NLD', 'NOR', 'SWE'
    },
    'Commercial Database': {
        'AUS', 'DNK', 'FIN', 'FRA', 'DEU', 'NLD', 'NOR', 'PRT', 'ESP', 'SWE'
    },
    'Proprietary': {
        'DNK', 'FIN', 'NOR', 'SWE'
    }
}


class CommaSeparatedList(BaseType):
    def to_native(self, value):
        return value.split(', ')

    def to_primitive(self, value):
        return ', '.join(value)


class Applicant(Model):
    id = StringType(required=True)
    country = StringType()


class IdentityReportItemPropertiesUK(Model):
    # The docs say it's this
    number_of_agencies = IntType()
    # But it's actually this...
    number_of_credit_agencies = IntType()


class IdentityReportItemPropertiesNonUK(Model):
    sources = CommaSeparatedList()


class IdentityReportItem(Model):
    result = StringType(choices=['clear', 'consider', 'unidentified'])


class IdentityReportItemUK(IdentityReportItem):
    properties = ModelType(IdentityReportItemPropertiesUK)

    def compute_matches(self, database_name, database_type, matched_fields):
        result = {
            'database_type': database_type,
        }
        if self.result == 'clear':
            result['matched_fields'] = matched_fields
            result['count'] = 1

            if database_type == 'CREDIT':
                num_matches = self.properties.number_of_agencies or self.properties.number_of_credit_agencies or 1
                return [{
                    'database_name': onfido_credit_source_name(i),
                    **result
                } for i in range(num_matches)]
        else:
            result['matched_fields'] = []
            result['count'] = 0

            if database_type == 'CREDIT':
                return [{
                    'database_name': onfido_credit_source_name(None),
                    **result
                }]

        return [{
            'database_name': database_name,
            **result
        }]


class IdentityReportItemNonUK(IdentityReportItem):
    properties = ModelType(IdentityReportItemPropertiesNonUK)

    def compute_matches(self, matched_fields):
        if self.result != 'clear':
            return []

        def map_source(source):
            if source == 'Credit Agencies':
                return {
                    'database_name': onfido_credit_source_name(0),
                    'database_type': 'CREDIT',
                    'matched_fields': matched_fields,
                    'count': 1,
                }
            else:
                return {
                    'database_name': source,
                    'database_type': 'CIVIL',
                    'matched_fields': matched_fields,
                    'count': 1,
                }

        return [map_source(source) for source in self.properties.sources]


class IdentityReportInnerBreakdown(Model):
    def compute_matches(self, matched_fields):
        raise NotImplementedError()


class IdentityReportInnerBreakdownUK(IdentityReportInnerBreakdown):
    credit_agencies = ModelType(IdentityReportItemUK)
    voting_register = ModelType(IdentityReportItemUK)
    telephone_database = ModelType(IdentityReportItemUK)

    @staticmethod
    def _claim_polymorphic(data):
        return 'credit_agencies' in data

    def compute_matches(self, matched_fields):
        matches = []
        if self.credit_agencies is not None:
            matches.extend(self.credit_agencies.compute_matches('Onfido', 'CREDIT', matched_fields))
        if self.voting_register is not None:
            matches.extend(self.voting_register.compute_matches('Voting Register', 'CIVIL', matched_fields))
        if self.telephone_database is not None:
            matches.extend(self.telephone_database.compute_matches('Telephone Database', 'CIVIL', matched_fields))
        return matches


class IdentityReportInnerBreakdownNonUK(IdentityReportInnerBreakdown):
    date_of_birth_matched = ModelType(IdentityReportItemNonUK)
    address_matched = ModelType(IdentityReportItemNonUK)

    @staticmethod
    def _claim_polymorphic(data):
        return 'date_of_birth_matched' in data or 'address_matched' in data

    def compute_matches(self, matched_fields):
        matches = []
        if self.date_of_birth_matched is not None:
            matches.extend(self.date_of_birth_matched.compute_matches(matched_fields))
        if self.address_matched is not None:
            matches.extend(self.address_matched.compute_matches(matched_fields))
        return matches


class IdentityReportInnerBreakdownSSN(IdentityReportInnerBreakdown):
    last_4_digits_match = ModelType(IdentityReportItem)
    full_match = ModelType(IdentityReportItem)

    @staticmethod
    def _claim_polymorphic(data):
        return 'last_4_digits_match' in data

    def compute_matches(self, matched_fields):
        matches = []
        if self.last_4_digits_match is not None and self.last_4_digits_match.result == 'clear':
            matches.append({
                'database_name': f'Social Security Database',
                'database_type': 'CIVIL',
                'matched_fields': matched_fields,
                'count': 1,
            })
        if self.full_match is not None and self.full_match == 'clear':
            matches.append({
                'database_name': f'Social Security Database',
                'database_type': 'CIVIL',
                'matched_fields': matched_fields,
                'count': 1,
            })
        return matches


class IdentityReportBreakdownItem(Model):
    result = StringType(choices=['clear', 'consider', 'unidentified'])
    breakdown = PolyModelType(IdentityReportInnerBreakdown, allow_subclasses=True)

    def compute_matches(self, matched_fields):
        return self.breakdown.compute_matches(matched_fields)


class IdentityReportBreakdown(Model):
    mortality = ModelType(IdentityReportItem)
    address = ModelType(IdentityReportBreakdownItem)
    date_of_birth = ModelType(IdentityReportBreakdownItem)
    ssn = ModelType(IdentityReportBreakdownItem)

    def compute_matches(self, country_code):
        matches = []
        if self.mortality is not None and self.mortality.result != 'clear':
            matches.append({
                'database_name': 'Mortality list',
                'database_type': 'MORTALITY',
                'matched_fields': ['FORENAME', 'SURNAME', 'DOB'],
                'count': 1,
            })

        if self.address is not None:
            matches.extend(self.address.compute_matches(['FORENAME', 'SURNAME', 'ADDRESS']))

        if self.date_of_birth is not None:
            matches.extend(self.date_of_birth.compute_matches(['FORENAME', 'SURNAME', 'DOB']))

        if self.ssn is not None:
            matches.extend(self.ssn.compute_matches(['FORNAME', 'SURNAME', 'ADDRESS']))

        all_databases = {match['database_name'] for match in matches}
        if onfido_credit_source_name(0) in all_databases:
            all_databases.add(onfido_credit_source_name(None))

        # Add mismatches
        for k, v in SUPPORTED_IDENTITY_DATABASES.items():
            if country_code in v and k not in all_databases:
                if k == onfido_credit_source_name(None):
                    database_type = 'CREDIT'
                else:
                    database_type = 'CIVIL'
                matches.append({
                    'database_name': k,
                    'database_type': database_type,
                    'matched_fields': [],
                    'count': 0,
                })

        return matches


class Report(Model):
    id = StringType(required=True)
    created_at = DateTimeType()
    name = StringType(choices=[
        'document', 'facial_similarity', 'identity', 'watchlist',
        'street_level', 'credit', 'criminal_history', 'right_to_work'
    ])
    href = StringType()
    status = StringType(choices=['awaiting_data', 'awaiting_approval', 'complete', 'withdrawn', 'paused', 'cancelled'])
    result = StringType(choices=['clear', 'consider', 'unidentified'])
    sub_result = StringType(choices=['clear', 'rejected', 'suspected', 'caution'])
    variant = StringType(choices=['standard', 'video', 'kyc', 'full', 'basic', 'enhanced'])


class IdentityReport(Report):
    breakdown = ModelType(IdentityReportBreakdown)

    @staticmethod
    def _claim_polymorphic(data):
        return data['name'] == 'identity'

    def compute_matches(self, country_code):
        return self.breakdown.compute_matches(country_code)


class Check(Model):
    id = StringType(required=True)
    created_at = DateTimeType()
    href = StringType()
    type = StringType(choices=['express', 'standard'])
    status = StringType(choices=['in_progress', 'awaiting_applicant', 'complete', 'withdrawn', 'paused', 'reopened'])
    tags = ListType(StringType)
    result = StringType(choices=['clear', 'consider'])
    download_uri = StringType()
    form_uri = StringType()
    redirect_uri = StringType()
    results_uri = StringType()
    reports = ListType(PolyModelType(Report, allow_subclasses=True))
