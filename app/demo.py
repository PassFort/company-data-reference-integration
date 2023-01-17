import json
import os
import re

from flask import Response
from werkzeug.exceptions import abort

from app.types.checks import CheckInput, RunCheckResponse
from app.types.common import (
    Charge,
    CheckedCompanyDataField,
    CommercialRelationshipType,
    CompanyFieldCheck,
    CompanyFieldCheckResult,
    DemoResultType,
)


def _try_load_demo_result(
    response_model, commercial_relationship: CommercialRelationshipType, name: str
):
    def _sanitize_filename(value: str, program=re.compile("^[a-z0-9A-Z_]+$")):
        if not program.match(value):
            abort(Response("Invalid demo request", status=400))
        return value

    filename = f"../static/demo_results/{_sanitize_filename(name)}.json"

    try:
        # Load file relative to current script
        with open(os.path.join(os.path.dirname(__file__), filename), "r") as file:
            raw_data = json.load(file)
            demo_response = response_model(**raw_data)
    except FileNotFoundError:
        return None

    if commercial_relationship == CommercialRelationshipType.PASSFORT:
        demo_response.charges = [
            Charge(**{"amount": 100, "reference": "DUMMY REFERENCE"}),
            Charge(**{"amount": 50, "sku": "NORMAL"}),
        ]

    return demo_response


def _run_demo_check(
    check_input: CheckInput,
    demo_result: str,
    commercial_relationship: CommercialRelationshipType,
) -> RunCheckResponse:
    if demo_result in {
        DemoResultType.ANY,
        DemoResultType.ANY_CHARGE,
        DemoResultType.COMPANY_INACTIVE,
        DemoResultType.COMPANY_NAME_MISMATCH,
        DemoResultType.COMPANY_NUMBER_MISMATCH,
        DemoResultType.COMPANY_ADDRESS_MISMATCH,
        DemoResultType.COMPANY_ADDRESS_MATCH,
        DemoResultType.COMPANY_COUNTRY_OF_INCORPORATION_MISMATCH,
    }:
        check_response = _try_load_demo_result(
            RunCheckResponse, commercial_relationship, DemoResultType.ALL_DATA
        )
    else:
        check_response = _try_load_demo_result(
            RunCheckResponse, commercial_relationship, f"{demo_result}"
        ) or _try_load_demo_result(
            RunCheckResponse, commercial_relationship, "UNSUPPORTED_DEMO_RESULT"
        )

    check_response.patch_to_match_input(check_input)

    if demo_result == DemoResultType.COMPANY_INACTIVE:
        check_response.check_output.metadata.is_active = False
        check_response.check_output.metadata.is_active_details = "Inactive"
    elif demo_result == DemoResultType.COMPANY_NAME_MISMATCH:
        check_response.check_output.metadata.name = (
            f"NOT {check_input.name}" if check_input.name else "Example Co."
        )
    elif demo_result == DemoResultType.COMPANY_NUMBER_MISMATCH:
        check_response.check_output.metadata.number = (
            f"NOT {check_input.number}" if check_input.number else "123456"
        )
    elif demo_result == DemoResultType.COMPANY_COUNTRY_OF_INCORPORATION_MISMATCH:
        check_response.check_output.metadata.country_of_incorporation = (
            "GBR" if check_input.country_of_incorporation != "GBR" else "FRA"
        )
    elif demo_result == DemoResultType.COMPANY_ADDRESS_MATCH:
        check_response.check_output.field_checks = [
            CompanyFieldCheck(
                **{
                    "field": CheckedCompanyDataField.ADDRESS,
                    "result": CompanyFieldCheckResult.MATCH,
                }
            )
        ]
    elif demo_result == DemoResultType.COMPANY_ADDRESS_MISMATCH:
        check_response.check_output.field_checks = [
            CompanyFieldCheck(
                **{
                    "field": CheckedCompanyDataField.ADDRESS,
                    "result": CompanyFieldCheckResult.MISMATCH,
                }
            )
        ]
    return check_response
