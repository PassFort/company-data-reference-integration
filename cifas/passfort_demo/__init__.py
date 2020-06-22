from typing import List
from passfort.cifas_check import CifasCheck, OutputData
from passfort.individual_data import IndividualData
from passfort.fraud_detection import FraudDetection, DatabaseType, FraudCase
from datetime import datetime
from time import time


def generate_refer_response() -> FraudDetection:
    return FraudDetection(
        search_reference=str(int(time())),
        match_count=2,
        database_type=DatabaseType.CIFAS,
        matches=[
            FraudCase(
                id='54673',
                reporting_company='Member Practice',
                case_type='Misuse of facility',
                product='Communications - Mobile Phone',
                do_not_filter=False,
                supply_date=datetime(year=2015, month=10, day=6),
                application_date=datetime(year=2014, month=12, day=17),
                claim_date=None,
                filing_reason=['Evasion of payment'],
                database_type=DatabaseType.CIFAS,
            ),
            FraudCase(
                id='54673',
                reporting_company='Member Practice',
                case_type='Misuse of facility',
                product='Communications - Mobile Phone',
                do_not_filter=False,
                supply_date=datetime(year=2015, month=9, day=9),
                application_date=datetime(year=2014, month=12, day=17),
                claim_date=None,
                filing_reason=['Evasion of payment'],
                database_type=DatabaseType.CIFAS,
            ),
        ]
    )


def generate_pass_response() -> FraudDetection:
    return FraudDetection(
        search_reference=str(int(time())),
        match_count=0,
        matches=[]
    )


def get_names(check: CifasCheck) -> List[str]:
    if isinstance(check.input_data, IndividualData):
        full_name = check.input_data.personal_details.name
        if full_name.given_names:
            names = [*full_name.given_names]
        else:
            names = []

        if full_name.family_name:
            names.append(full_name.family_name)
        return names
    else:
        metadata = check.input_data.metadata
        if metadata and metadata.name:
            return [metadata.name]
    return []


def has_match(check: CifasCheck) -> bool:
    return any((
        'refer' in name.lower()
        for name in get_names(check)
    ))


def get_demo_response(check: CifasCheck) -> OutputData:
    return OutputData(
        fraud_detection=generate_refer_response() if has_match(check) else generate_pass_response()
    )
