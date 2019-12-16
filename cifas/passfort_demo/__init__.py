from typing import List, Union
from passfort.cifas_check import CifasCheck, OutputData
from passfort.individual_data import IndividualData
from passfort.company_data import CompanyData
from passfort.fraud_detection import FraudDetection
from os import path


def get_names(check: CifasCheck) -> List[str]:
    if isinstance(check.input_data, IndividualData):
        full_name = check.input_data.personal_details.name
        if full_name.given_names:
            names = [*full_name.given_names]
        else:
            names = []

        if full_name.family_name:
            names.append(full_name.family_name)
    return []


def has_match(check: CifasCheck) -> bool:
    return any((
        'refer' not in name.lower()
        for name in get_names(check)
    ))


def get_demo_response(check: CifasCheck) -> OutputData:
    return OutputData(
        fraud_detection=FraudDetection(
            search_reference='111111111',
            match_count=1 if has_match(check) else 0,
        ),
    )
