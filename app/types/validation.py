import inspect
from dataclasses import dataclass
from functools import wraps
from typing import Iterable, List, Optional, Type, TypeVar

from flask import abort, jsonify, make_response, request
from pydantic import BaseModel, ValidationError

from app.types.checks import RunCheckRequest
from app.types.common import (
    SUPPORTED_COUNTRIES,
    Error,
    ErrorType,
    LocalField,
    SearchRequest,
)

T = TypeVar("T")


@dataclass
class SearchInput:
    country_of_incorporation: str


def _validate_country_of_incorporation(country_code) -> List[Error]:
    errors = []
    if country_code is None:
        errors.append(Error.missing_required_field(LocalField.COUNTRY_OF_INCORPORATION))
    if country_code not in SUPPORTED_COUNTRIES:
        errors.append(Error.unsupported_country())
    return errors


def _validate_demo_check(demo_result, demo_type_label):
    errors = []
    if demo_result is None:
        errors.append(
            Error(
                **{
                    "type": ErrorType.PROVIDER_MESSAGE,
                    "message": f"Live {demo_type_label} is not supported",
                }
            )
        )
    return errors


def validate_search_request(request: SearchRequest) -> List[Error]:
    errors = _validate_country_of_incorporation(
        request.search_input.country_of_incorporation
    )
    errors.extend(_validate_demo_check(request.demo_result, "search"))
    return errors


def validate_check_request(request: RunCheckRequest) -> List[Error]:
    errors = _validate_country_of_incorporation(
        request.check_input.get_country_of_incorporation()
    )
    errors.extend(_validate_demo_check(request.demo_result, "check"))
    return errors


def validate_poll_request(request, check_id=None, reference=None):
    errors = []
    if check_id is not None and check_id != request.id:
        errors.append(
            [
                Error(
                    type=ErrorType.INVALID_CHECK_INPUT,
                    message="ID in URL mismatches check ID in request",
                )
            ]
        )
    if reference is not None and reference != request.reference:
        errors.append(
            [
                Error(
                    type=ErrorType.INVALID_CHECK_INPUT,
                    message="Reference in URL mismatches reference in request",
                )
            ]
        )
    return errors


def _first(x: Iterable[T]) -> Optional[T]:
    return next(iter(x), None)


def _get_input_annotation(signature: inspect.Signature) -> Optional[Type[BaseModel]]:
    first_param: Optional[inspect.Parameter] = _first(signature.parameters.values())
    if first_param is None:
        return None

    if first_param.kind not in [
        inspect.Parameter.POSITIONAL_ONLY,
        inspect.Parameter.POSITIONAL_OR_KEYWORD,
    ]:
        return None

    if not issubclass(first_param.annotation, BaseModel):
        return None

    return first_param.annotation


def validate_models(fn):
    """
    Creates a Pydantic Model from the request data and validates it.

    Throws DataError if invalid.
    Otherwise, it passes the validated request data to the wrapped function.
    """

    signature = inspect.signature(fn)

    assert issubclass(
        signature.return_annotation, BaseModel
    ), "Must have a return type annotation"
    output_model = signature.return_annotation
    input_model = _get_input_annotation(signature)

    @wraps(fn)
    def wrapped_fn(*args, **kwargs):
        if input_model is None:
            res = fn(*args, **kwargs)
        else:
            model = None
            try:
                model = input_model(**request.json)
            except ValidationError as e:
                abort(
                    make_response(
                        jsonify(
                            {
                                "errors": [
                                    {
                                        "message": error["msg"],
                                        "type": ErrorType.INVALID_INPUT,
                                    }
                                    for error in e.errors()
                                ]
                            }
                        ),
                        400,
                    )
                )

            res = fn(model, *args, **kwargs)

        assert isinstance(res, output_model)

        return res.dict(exclude_none=True)

    return wrapped_fn
