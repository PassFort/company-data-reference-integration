from typing import List, Optional
from datetime import date
from dataclasses import dataclass, field
from dataclasses_json import config
from enum import Enum


class DatabaseType(Enum):
    CIFAS = 'CIFAS'


@dataclass
class FraudCase:
    id: str
    reporting_company: str
    case_type: str
    product: str
    do_not_filter: bool
    supply_date: Optional[date] = field(
        metadata=config(
            encoder=lambda value: value and date.isoformat(value)
        )
    )
    application_date: Optional[date] = field(
        metadata=config(
            encoder=lambda value: value and date.isoformat(value)
        )
    )
    claim_date: Optional[date] = field(
        metadata=config(
            encoder=lambda value: value and date.isoformat(value)
        )
    )
    filing_reason: List[str]
    database_type: DatabaseType = DatabaseType.CIFAS


@dataclass
class FraudDetection:
    search_reference: str
    match_count: int
    matches: List[FraudCase]
    database_type: DatabaseType = DatabaseType.CIFAS
