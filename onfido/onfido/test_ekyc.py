import unittest
from onfido.ekyc import onfido_to_source_counts, get_report_from_check, source_counts_to_individual, onfido_check_to_individual
from onfido.mock_data.ekyc import mock_uk_check, mock_usa_check, mock_usa_ssn_fail_check


class TestOnfioRequests(unittest.TestCase):
    def test_onfido_to_source_counts(self):
        mock_report = get_report_from_check(mock_uk_check['data'])
        source_counts = onfido_to_source_counts(mock_report)
        self.assertEqual(source_counts, mock_uk_check['expected_source_count'])

    def test_source_counts_to_individual(self):
        individual = source_counts_to_individual(mock_uk_check['expected_source_count'])

        self.assertEqual(individual, {
            'db_matches': mock_uk_check['expected_database_matches'],
            'credit_ref': mock_uk_check['expected_credit_ref']
        })

    # test that compose function works as expected
    def test_onfido_check_to_individual(self):
        individual = onfido_check_to_individual(mock_uk_check['data'])
        self.maxDiff = None

        self.assertEqual({
            'db_matches': mock_uk_check['expected_database_matches'],
            'credit_ref': mock_uk_check['expected_credit_ref']
        }, individual)

    def test_usa_onfido_to_source_counts(self):
        mock_report = get_report_from_check(mock_usa_check['data'])
        source_counts = onfido_to_source_counts(mock_report)
        self.assertEqual(source_counts, mock_usa_check['expected_source_count'])

    def test_usa_no_ssn_onfido_to_source_counts(self):
        mock_report = get_report_from_check(mock_usa_ssn_fail_check['data'])
        source_counts = onfido_to_source_counts(mock_report)
        self.assertEqual(source_counts, mock_usa_ssn_fail_check['expected_source_count'])

    def test_usa_onfido_to_individual(self):
        individual = onfido_check_to_individual(mock_usa_check['data'])
        self.assertEqual(individual, {
            'db_matches': mock_usa_check['expected_database_matches'],
            'credit_ref': mock_usa_check['expected_credit_ref']
        })
