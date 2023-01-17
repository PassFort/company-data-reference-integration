import inspect
from dataclasses import dataclass
from functools import wraps
from typing import TypeVar, Iterable, Optional, Type, Tuple, List

from flask import request, abort, Response, jsonify
from schematics import Model
from schematics.exceptions import DataError

from app.types.checks import CheckInput, RunCheckRequest
from app.types.common import Error, Field

T = TypeVar('T')


@dataclass
class SearchInput:
    country_of_incorporation: str


def _first(x: Iterable[T]) -> Optional[T]:
    return next(iter(x), None)


def _get_input_annotation(signature: inspect.Signature) -> Optional[Type[Model]]:
    first_param: Optional[inspect.Parameter] = _first(
        signature.parameters.values())
    if first_param is None:
        return None

    if first_param.kind not in [inspect.Parameter.POSITIONAL_ONLY, inspect.Parameter.POSITIONAL_OR_KEYWORD]:
        return None

    if not issubclass(first_param.annotation, Model):
        return None

    return first_param.annotation


def validate_models(fn):
    """
3    Creates a Schematics Model from the request data and validates it.

    Throws DataError if invalid.
    Otherwise, it passes the validated request data to the wrapped function.
    """

    signature = inspect.signature(fn)

    assert issubclass(signature.return_annotation,
                      Model), 'Must have a return type annotation'
    output_model = signature.return_annotation
    input_model = _get_input_annotation(signature)

    @wraps(fn)
    def wrapped_fn(*args, **kwargs):
        if input_model is None:
            res = fn(*args, **kwargs)
        else:
            model = None
            try:
                model = input_model().import_data(request.json, apply_defaults=True)
                model.validate()
            except DataError as e:
                abort(Response(str(e), status=400))

            res = fn(model, *args, **kwargs)

        assert isinstance(res, output_model)

        return jsonify(res.serialize())

    return wrapped_fn


def _extract_check_input(req: RunCheckRequest) -> Tuple[List[Error], Optional[CheckInput]]:
    errors = []

    # Extract country of incorporation
    country_of_incorporation = req.check_input.get_country_of_incorporation()
    if country_of_incorporation is None:
        errors.append(Error.missing_required_field(Field.COUNTRY_OF_INCORPORATION))

    name = req.check_input.get_company_name()
    number = req.check_input.get_company_number()

    if errors:
        return errors, None
    else:
        return [], CheckInput(
            name=name,
            number=number,
            country_of_incorporation=country_of_incorporation,
        )


def _extract_search_input(req: RunCheckRequest) -> Tuple[List[Error], Optional[SearchInput]]:
    errors = []

    # Extract country of incorporation
    country_of_incorporation = req.search_input.country_of_incorporation
    if country_of_incorporation is None:
        errors.append(Error.missing_required_field(Field.COUNTRY_OF_INCORPORATION))

    if errors:
        return errors, None
    else:
        return [], SearchInput(
            country_of_incorporation=country_of_incorporation
        )
