from flask import Blueprint

from app.api.auth import auth
from app.demo import _try_load_demo_result
from app.types.common import (
    SUPPORTED_COUNTRIES,
    CommercialRelationshipType,
    DemoResultType,
    Error,
    ErrorType,
    SearchRequest,
    SearchResponse,
)
from app.types.validation import _extract_search_input, validate_models

search_api = Blueprint("search", __name__)


@search_api.route("/search", methods=["POST"])
@auth.login_required
@validate_models
def search(req: SearchRequest) -> SearchResponse:
    errors, search_input = _extract_search_input(req)
    if errors:
        return SearchResponse.error(errors)

    country = search_input.country_of_incorporation
    if country not in SUPPORTED_COUNTRIES:
        return SearchResponse.error([Error.unsupported_country()])

    if req.demo_result is not None:
        return _run_demo_search(req.demo_result, req.commercial_relationship)

    return SearchResponse.error(
        [
            Error(
                {
                    "type": ErrorType.PROVIDER_MESSAGE,
                    "message": "Live searches are not supported",
                }
            )
        ]
    )


def _run_demo_search(
    demo_result: str, commercial_relationship: CommercialRelationshipType
) -> SearchResponse:
    # Default to full match if we can return any result
    if demo_result in {DemoResultType.ANY}:
        demo_result = DemoResultType.MANY_HITS

    return _try_load_demo_result(
        SearchResponse, commercial_relationship, f"{demo_result}"
    ) or _try_load_demo_result(
        SearchResponse, commercial_relationship, "UNSUPPORTED_DEMO_RESULT"
    )
