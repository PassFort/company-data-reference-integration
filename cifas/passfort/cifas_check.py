from typing import Union, List, Dict, Optional
from enum import Enum
from collections.abc import Mapping
from dataclasses import dataclass, field
from dataclasses_json import dataclass_json, config
from passfort import EntityType, union_field
from passfort.individual_data import IndividualData
from passfort.company_data import CompanyData
from passfort.date import PartialDate


@dataclass
class CifasConfig:
    product_code: str
    search_type: str
    requesting_institution: int
    use_uat: bool


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
