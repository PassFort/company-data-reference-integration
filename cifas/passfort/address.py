from typing import Optional
from dataclasses import dataclass


@dataclass
class Address:
    street_number: Optional[str] = None
    premise: Optional[str] = None
    subpremise: Optional[str] = None
    route: Optional[str] = None
    locality: Optional[str] = None
    postal_town: Optional[str] = None
    postal_code: Optional[str] = None
    country: Optional[str] = None


@dataclass
class AddressHistoryItem:
    address: Address
