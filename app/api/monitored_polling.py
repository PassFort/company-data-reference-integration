import json
import logging
import os.path
import tempfile
import uuid

from flask import Blueprint, abort, make_response, send_file

from app.demo import _run_demo_check
from app.files import static_file_path
from app.types.checks import (
    CheckPollRequest,
    MonitoredCheckPollResponse,
    MonitoredCheckRequest,
    MonitoredCheckResponse,
    MonitoredPollResponse,
    RunCheckRequest,
    StartCheckResponse,
)
from app.types.common import Error, ErrorType
from app.types.validation import (
    validate_check_request,
    validate_models,
    validate_poll_reference,
    validate_poll_request,
)

from .auth import auth
from .metadata import metadata_api

logger = logging.getLogger(__name__)
monitored_polling_api = Blueprint(
    "monitored_polling", __name__, url_prefix="/monitored-polling"
)
monitored_polling_api.register_blueprint(metadata_api)

# arbitrary ID generated to uniquely identify this reference integration
PROVIDER_ID = "b4165f9c-8d21-11ed-90f6-4f528b1df65f"
TEMP_DIRECTORY = tempfile.gettempdir()


def save_reference_data(reference, data, create=True):
    response_data_path = os.path.join(TEMP_DIRECTORY, f"{reference}.json")
    logger.debug("Saving reference data at %s", response_data_path)
    if create or os.path.isfile(response_data_path):
        with open(response_data_path, "w") as handle:
            json.dump(data.dict(), handle)
        return True
    return False


def load_reference_data(reference):
    response_data_path = os.path.join(TEMP_DIRECTORY, f"{reference}.json")
    logger.debug("Loading reference data at %s", response_data_path)
    with open(response_data_path, "r") as handle:
        response_data = json.load(handle)
    return response_data


@monitored_polling_api.route("/config")
@auth.login_required
def get_config():
    return send_file(static_file_path("config.monitored-polling.json"), max_age=-1)


@monitored_polling_api.route("/checks", methods=["POST"])
@auth.login_required
@validate_models
def run_check(req: RunCheckRequest) -> StartCheckResponse:
    errors = validate_check_request(req)
    if errors:
        return StartCheckResponse.error(errors, provider_id=PROVIDER_ID)

    demo_data: MonitoredCheckPollResponse = _run_demo_check(
        req.required_check_input,
        req.demo_result,
        req.commercial_relationship,
        response_class=MonitoredCheckPollResponse,
    )
    if demo_data is None:
        abort(make_response("Could not load unsupported demo result", 500))

    # randomly generate a temp file and use its name as the reference
    # polling will check this temp file and report it back.
    # there's a separate private API endpoint to modify this temp file.
    reference = str(uuid.uuid4())
    # saving the reference into the check output for easy testing.
    # allows for updating the check output via _update API below.
    if demo_data.check_output:
        demo_data.check_output.external_refs.generic = reference
    save_reference_data(reference, demo_data)

    return StartCheckResponse(reference=reference, provider_id=PROVIDER_ID)


@monitored_polling_api.route("/checks/<check_id>/poll", methods=["POST"])
@auth.login_required
@validate_models
def checks_poll(
    request: CheckPollRequest,
    **route_kwargs,
) -> MonitoredCheckPollResponse:
    errors = validate_poll_request(request, **route_kwargs)
    if errors:
        return MonitoredCheckPollResponse.error(
            errors, check_output=None, provider_id=PROVIDER_ID
        )

    cur_poll_data = load_reference_data(request.reference)
    return MonitoredCheckPollResponse(**cur_poll_data)


@monitored_polling_api.route("/monitored_provider/poll", methods=["POST"])
@auth.login_required
@validate_models
def monitored_provider_poll() -> MonitoredPollResponse:
    return MonitoredPollResponse()


@monitored_polling_api.route("/monitored_checks/<reference>/poll", methods=["POST"])
@auth.login_required
@validate_models
def monitored_checks_poll(
    request: MonitoredCheckRequest,
    reference="",
) -> MonitoredCheckPollResponse:
    errors = validate_poll_request(request, reference=reference)
    if errors:
        return MonitoredCheckPollResponse.error(
            errors, check_output=None, provider_id=PROVIDER_ID
        )

    cur_poll_data = load_reference_data(reference)
    return MonitoredCheckPollResponse(**cur_poll_data)


@monitored_polling_api.route("/monitored_checks/<reference>/ready", methods=["POST"])
@auth.login_required
@validate_models
def monitored_checks_ready(
    request: MonitoredCheckRequest,
    **route_kwargs,
) -> MonitoredCheckResponse:
    errors = validate_poll_request(request, **route_kwargs)
    if errors:
        return MonitoredCheckResponse.error(errors, provider_id=PROVIDER_ID)

    # This is always ready
    return MonitoredCheckResponse()


#####################################
# PRIVATE - FOR INTERNAL TESTING ONLY
#####################################
@monitored_polling_api.route("/monitored_checks/<reference>/_update", methods=["POST"])
@auth.login_required
@validate_models
def monitored_checks_update(
    updated_response: MonitoredCheckPollResponse,
    reference="",
) -> MonitoredCheckResponse:
    errors = validate_poll_reference(reference)
    if errors:
        return MonitoredCheckResponse.error(errors, provider_id=PROVIDER_ID)
    saved = save_reference_data(reference, updated_response, create=False)
    if not saved:
        MonitoredCheckResponse.error(
            [
                Error(
                    type=ErrorType.INVALID_INPUT,
                    message="Could not update reference",
                    data={"reference": reference},
                )
            ]
        )
    return MonitoredCheckResponse()
