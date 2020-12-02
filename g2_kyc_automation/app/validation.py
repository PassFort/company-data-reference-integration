import logging

from flask import (
    abort,
    request,
)
from functools import wraps
from flask.json import jsonify
from schematics.exceptions import DataError
from app.types import Error


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
                model = validation_model().import_data(
                    request.json, apply_defaults=True
                )
                model.validate()
            except DataError as e:
                errors = e.to_primitive()
                if errors.get("credentials") is not None:
                    response = jsonify({"errors": Error.provider_misconfiguration_error(
                        "No credentials provided")})
                else:
                    response = jsonify({"errors": Error.bad_api_request(e)})
                abort(response)

            return fn(model, *args, **kwargs)

        return wrapped_fn

    return validates_model
