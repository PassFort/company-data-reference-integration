from dataclasses import dataclass
from typing import Optional, List

from schematics.types import UUIDType, ModelType, ListType, BaseType

from app.types.common import BaseModel, DemoResultType, CommercialRelationshipType, CompanyData, ProviderConfig, \
    ProviderCredentials, Error, Warn, Charge


class RunCheckRequest(BaseModel):
    id = UUIDType(required=True)
    demo_result = DemoResultType(default=None)
    commercial_relationship = CommercialRelationshipType(required=True)
    check_input: CompanyData = ModelType(CompanyData, required=True)
    provider_config: ProviderConfig = ModelType(ProviderConfig, required=True)
    provider_credentials: Optional[ProviderCredentials] = ModelType(
        ProviderCredentials, default=None)


class RunCheckResponse(BaseModel):
    check_output: Optional[CompanyData] = ModelType(CompanyData, default=None)
    errors: List[Error] = ListType(ModelType(Error), default=[])
    warnings: List[Warn] = ListType(ModelType(Warn), default=[])
    provider_data = BaseType(default=None)
    charges = ListType(ModelType(Charge), default=[])

    @staticmethod
    def error(errors: List[Error]) -> 'RunCheckResponse':
        res = RunCheckResponse()
        res.errors = errors
        return res

    def patch_to_match_input(self, check_input):
        if self.check_output:
            if self.check_output.metadata:
                self.check_output.metadata.country_of_incorporation = (
                        check_input.country_of_incorporation or self.check_output.metadata.country_of_incorporation
                )
                self.check_output.metadata.name = check_input.name or self.check_output.metadata.name
                self.check_output.metadata.number = check_input.number or self.check_output.metadata.number


@dataclass
class CheckInput:
    name: Optional[str]
    number: Optional[str]
    country_of_incorporation: Optional[str]
