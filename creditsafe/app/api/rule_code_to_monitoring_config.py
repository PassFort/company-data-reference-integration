from enum import Enum, unique

@unique
class MonitoringConfigType(Enum):
    ASSESS_FINANCIAL_DATA = 'assess_financial_data'
    IDENTIFY_OFFICERS = 'identify_officers'
    VERIFY_COMPANY_DETAILS = 'verify_company_details'


rule_code_to_monitoring_config = {
    101: MonitoringConfigType.ASSESS_FINANCIAL_DATA,
    102: MonitoringConfigType.ASSESS_FINANCIAL_DATA,
    104: MonitoringConfigType.VERIFY_COMPANY_DETAILS,
    105: MonitoringConfigType.VERIFY_COMPANY_DETAILS,
    107: MonitoringConfigType.IDENTIFY_OFFICERS
}
