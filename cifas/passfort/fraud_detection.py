from dataclasses import dataclass, field
from enum import Enum


class DatabaseType(Enum):
    CIFAS = 'CIFAS'


@dataclass
class FraudDetection:
    search_reference: str
    match_count: int 
    database_type: DatabaseType = DatabaseType.CIFAS
