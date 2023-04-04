import base64
from datetime import datetime, timezone
from functools import wraps
import logging
from uuid import UUID

from flask import abort, request

from app.http_signature import HTTPSignatureAuth
from app.startup import integration_key_store, INTEGRATION_SECRET_KEY
from app.auth.signed_urls import QUERY_PARAMS, verify_signed_url

http_sig = HTTPSignatureAuth()

@http_sig.resolve_key
def resolve_key(key_id):
    return integration_key_store.get(key_id)

# Authentication decorator
def require_signed_url(f):
    @wraps(f)
    def decorator(*args, **kwargs):
        version = request.args.get("version")
        if version != "1" :
            logging.warning(
                f"Attempt to access external resource via unsupported auth scheme (version `{version}`)"
            )
            abort(400, "Integration was built to only support version `1` of the signed url scheme")

        if list(request.args.keys()) != QUERY_PARAMS:
            abort(400, "A signed URL should have the query params `version`, `valid_until`, `auditee_id`, `signature`")

        for param in QUERY_PARAMS:
            if len(request.args.getlist(param)) != 1:
                abort(400, "Each query param in a signed URL should appear exactly once")

        try:
            valid_until = datetime.fromtimestamp(int(request.args.get("valid_until")))
            if valid_until < datetime.now():
                abort(404, "Signed URL no longer valid") 
        except ValueError:
            abort(404)

        try:
            auditee_id = UUID(request.args.get("auditee_id"))
        except ValueError:
            abort(400, "Auditee ID must be a valid UUID")


        if not verify_signed_url(base64.b64decode(INTEGRATION_SECRET_KEY), request.url):
            abort(404)
        
        return f(*args, **kwargs)
    return decorator

