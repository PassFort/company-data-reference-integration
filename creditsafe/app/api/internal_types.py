from schematics import Model
from schematics.types import BooleanType, StringType, ModelType, ListType


class CreditSafeCompanySearchResponse(Model):
    credit_safe_id = StringType(required=True, serialized_name="id")
    registration_number = StringType(default=None, serialized_name="regNo")
    name = StringType(required=True)

    def as_passfort_format(self, country, state):
        result = {
            'name': self.name,
            'number': self.registration_number,
            'creditsafe_id': self.credit_safe_id,
            'country_of_incorporation': country
        }
        if state:
            result['state_of_incorporation'] = state
        return result


    @classmethod
    def from_json(cls, data):
        model = cls().import_data(data, apply_defaults=True)
        model.validate()
        return model
