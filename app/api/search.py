from flask import Blueprint

from app.api.auth import auth
from app.demo import _try_load_demo_result
from app.types.common import (
    CommercialRelationshipType,
    DemoResultType,
    SearchRequest,
    SearchResponse,
)
from app.types.validation import validate_models, validate_search_request

search_api = Blueprint("search", __name__)


@search_api.route("/search", methods=["POST"])
@auth.login_required
@validate_models
def search(req: SearchRequest) -> SearchResponse:
    errors = validate_search_request(req)
    if errors:
        return SearchResponse.error(errors)

    return _run_demo_search(req.demo_result, req.commercial_relationship)


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
