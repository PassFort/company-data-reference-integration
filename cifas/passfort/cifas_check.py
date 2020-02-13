from typing import Union, List, Dict, Optional
from enum import Enum
from collections.abc import Mapping
from dataclasses import dataclass, field
from dataclasses_json import dataclass_json, config
from passfort import EntityType, union_field, coerce_integer
from passfort.individual_data import IndividualData
from passfort.company_data import CompanyData
from passfort.date import PartialDate
from passfort.fraud_detection import FraudDetection
from passfort.error import Error


@dataclass
class CifasConfig:
    product_code: str
    use_uat: bool
    user_name: str
    search_type: str = 'XX'
    member_id: int = coerce_integer()


@dataclass
class CifasCredentials:
    cert: str


@dataclass_json
@dataclass
class CifasCheck:
    config: CifasConfig
    credentials: CifasCredentials
    input_data: Union[IndividualData, CompanyData] = union_field(
        IndividualData, 
        CompanyData, 
        tag='entity_type',
    )

    is_demo: bool = False


@dataclass_json
@dataclass
class OutputData:
    fraud_detection: FraudDetection 


@dataclass_json
@dataclass
class CifasCheckResponse:
    output_data: Optional[OutputData]
    errors: List[Error] = field(default_factory=list)
