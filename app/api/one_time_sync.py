from flask import Blueprint, send_file

from app.auth import http_sig, require_signed_url
from app.api.metadata import metadata_api
from app.api.search import search_api
from app.demo import _run_demo_check
from app.files import static_file_path
from app.types.checks import RunCheckRequest, RunCheckResponse
from app.types.validation import validate_check_request, validate_models

one_time_sync_api = Blueprint("one_time_sync", __name__)
one_time_sync_api.register_blueprint(search_api)
one_time_sync_api.register_blueprint(metadata_api)

@one_time_sync_api.route("/external_resource")
@require_signed_url
def linked_hello_world():
    return "Hello, World!"

@one_time_sync_api.route("/config")
@http_sig.login_required
def get_config():
    return send_file(static_file_path("config.one-time-sync.json"), max_age=-1)


@one_time_sync_api.route("/checks", methods=["POST"])
@http_sig.login_required
@validate_models
def run_check(req: RunCheckRequest) -> RunCheckResponse:
    errors = validate_check_request(req)
    if errors:
        return RunCheckResponse.error(errors)

    return _run_demo_check(
        req.required_check_input, req.demo_result, req.commercial_relationship
    )
