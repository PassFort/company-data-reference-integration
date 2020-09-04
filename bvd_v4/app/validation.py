from flask import (
    abort,
    request,
)
from functools import wraps
from schematics.exceptions import (
    DataError,
)


def request_model(validation_model):
    """
    Creates a Schematics Model from the request data and validates it.

    Throws DataError if invalid.
    Otherwise, it passes the validated request data to the wrapped function.
    """

    def validates_model(fn):
        @wraps(fn)
        def wrapped_fn(*args, **kwargs):
            model = None
            try:
                model = validation_model().import_data(request.json, apply_defaults=True)
                model.validate()
            except DataError as e:
                abort(400, e.to_primitive())
            return fn(model, *args, **kwargs)

        return wrapped_fn

    return validates_model


def response_model(validation_model):
    """
    Creates a Schematics Model from the response data and validates it.

    Throws DataError if invalid.
    Otherwise, it returns the validated response data to the calling function.
    """

    def fetches_model(fn):
        @wraps(fn)
        def wrapped_fn(*args, **kwargs):
            model = None
            response = fn(*args, **kwargs)
            try:
                model = validation_model().import_data(response.json(), apply_defaults=True)
                model.validate()
                return model
            except DataError as e:
                abort(500, e.to_primitive())

        return wrapped_fn

    return fetches_model
