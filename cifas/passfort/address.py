from typing import Optional
from dataclasses import dataclass
from passfort import coerce_empty_string


@dataclass
class Address:
    street_number: Optional[str] = coerce_empty_string()
    premise: Optional[str] = coerce_empty_string()
    subpremise: Optional[str] = coerce_empty_string()
    route: Optional[str] = coerce_empty_string()
    locality: Optional[str] = coerce_empty_string()
    postal_town: Optional[str] = coerce_empty_string()
    postal_code: Optional[str] = coerce_empty_string()
    country: Optional[str] = coerce_empty_string()


@dataclass
class AddressHistoryItem:
    address: Address
