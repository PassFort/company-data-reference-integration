from dataclasses import dataclass


@dataclass
class CifasSearch:
    member_search_reference: str
    search_reference: int
    has_match: bool
