from dataclasses import dataclass
from typing import List, Optional

from app.types.common import (
    UUID,
    Charge,
    CompanyData,
    OperationRequest,
    OperationResponse,
)


@dataclass
class CheckInput:
    name: Optional[str]
    number: Optional[str]
    country_of_incorporation: Optional[str]


class RunCheckRequest(OperationRequest):
    id: UUID
    check_input: CompanyData

    @property
    def required_check_input(self) -> CheckInput:
        country_of_incorporation = self.check_input.get_country_of_incorporation()
        name = self.check_input.get_company_name()
        number = self.check_input.get_company_number()
        return CheckInput(
            name=name,
            number=number,
            country_of_incorporation=country_of_incorporation,
        )


class RunCheckResponse(OperationResponse):
    check_output: Optional[CompanyData]
    charges: List[Charge] = []

    def patch_to_match_input(self, check_input: CheckInput):
        if self.check_output and self.check_output.metadata:
            self.check_output.metadata.country_of_incorporation = (
                check_input.country_of_incorporation
                or self.check_output.metadata.country_of_incorporation
            )
            self.check_output.metadata.name = (
                check_input.name or self.check_output.metadata.name
            )
            self.check_output.metadata.number = (
                check_input.number or self.check_output.metadata.number
            )
