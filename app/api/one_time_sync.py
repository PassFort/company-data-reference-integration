from flask import Blueprint, send_file

from app.api.auth import auth
from app.api.metadata import metadata_api
from app.api.search import search_api
from app.demo import _run_demo_check
from app.types.checks import RunCheckRequest, RunCheckResponse
from app.types.common import SUPPORTED_COUNTRIES, Error, ErrorType
from app.types.validation import _extract_check_input, validate_models

one_time_sync_api = Blueprint("one_time_sync", __name__)
one_time_sync_api.register_blueprint(search_api)
one_time_sync_api.register_blueprint(metadata_api)


@one_time_sync_api.route("/config")
@auth.login_required
def get_config():
    return send_file("../static/config.json", cache_timeout=-1)


@one_time_sync_api.route("/checks", methods=["POST"])
@auth.login_required
@validate_models
def run_check(req: RunCheckRequest) -> RunCheckResponse:
    errors, check_input = _extract_check_input(req)
    if errors:
        return RunCheckResponse.error(errors)

    country = check_input.country_of_incorporation
    if country not in SUPPORTED_COUNTRIES:
        return RunCheckResponse.error([Error.unsupported_country()])

    if req.demo_result is not None:
        return _run_demo_check(
            check_input, req.demo_result, req.commercial_relationship
        )

    return RunCheckResponse.error(
        [
            Error(
                {
                    "type": ErrorType.PROVIDER_MESSAGE,
                    "message": "Live checks are not supported",
                }
            )
        ]
    )
