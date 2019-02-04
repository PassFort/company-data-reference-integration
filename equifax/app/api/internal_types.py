from schematics.models import Model
from schematics.types import ModelType, ListType, StringType, UnionType

from .types import ErrorCode


class EquifaxErrorDetails(Model):
    error_code = StringType(serialized_name='ErrorCode', default=None)
    source_code = StringType(serialized_name='SourceCode', default=None)
    additional_information = StringType(serialized_name='AdditionalInformation', default=None)
    description = StringType(serialized_name='Description', required=True)

    def as_passfort_error(self):
        internal_error_code = ErrorCode.MISCONFIGURATION_ERROR.value if self.error_code == 'E0819' \
            else ErrorCode.PROVIDER_UNKNOWN_ERROR.value
        message = f'{self.description}'
        if self.additional_information:
            message = f'{message} ({self.additional_information})'

        return {
            'code': internal_error_code,
            'source': 'PROVIDER',
            'message': message
        }


class EquifaxError(Model):
    error = UnionType(
        (
            ModelType(EquifaxErrorDetails, default=None),
            ListType
        ),
        field=ModelType(EquifaxErrorDetails),
        serialized_name='Error')

    def as_passfort_errors(self):
        if isinstance(self.error, list):
            return [e.as_passfort_error() for e in self.error]
        else:
            return [self.error.as_passfort_error()]


class EquifaxErrorReport(Model):
    errors = ModelType(EquifaxError, serialized_name='Errors', default=None)


class EquifaxResponse(Model):
    error_report = ModelType(EquifaxErrorReport, serialized_name='CNErrorReport', default=None)

    def get_errors(self):
        if self.error_report and self.error_report.errors and self.error_report.errors.error:
            return self.error_report.errors.as_passfort_errors()
        return []


class EquifaxResponseWithRoot(Model):
    root = ModelType(EquifaxResponse, serialized_name='EfxTransmit', default=None)

    @classmethod
    def from_json(cls, data):
        model = cls().import_data(data, apply_defaults=True)
        model.validate()
        return model

    def get_errors(self):
        return self.root.get_errors()
