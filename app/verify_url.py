import base64
import hashlib
import hmac
import logging
from urllib.parse import urlparse, parse_qs, urlencode

# from app.startup import _env

# key = _env("INTEGRATION_SECRET_KEY")
# key = b"my_secret_key"

QUERY_PARAMS = ["version", "valid_until", "auditee_id", "signature"] 

def get_query_parameter_value(url, query_name):
    parsed_url = urlparse(url)
    return parse_qs(parsed_url.query)[query_name][0]

def remove_query_parameter(url, query_name):
    parsed_url = urlparse(url)
    query = parse_qs(parsed_url.query)
    query.pop(query_name, None)
    return parsed_url._replace(query=urlencode(query, True)).geturl()

def compute_signature(key, unsigned_url):
    return hmac.new(
        key,
        bytes(unsigned_url, encoding='utf-8'),
        digestmod=hashlib.sha256
    ).digest()


def verify_signed_url(key, signed_url):
    unsigned_url = remove_query_parameter(signed_url, "signature")

    computed_signature = compute_signature(key, unsigned_url)

    received_signature = base64.urlsafe_b64decode(get_query_parameter_value(signed_url, "signature"))
    
    signature_valid = hmac.compare_digest(computed_signature, received_signature)
    if not signature_valid:
        logging.warning(f'Signature mismatch: (computed {computed_signature}, received {received_signature})')
    return signature_valid
