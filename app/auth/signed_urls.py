import base64
import hashlib
import hmac
import logging

QUERY_PARAMS = ["version", "valid_until", "auditee_id", "signature"] 

def pop_query_parameter(url, name):
    from urllib.parse import urlparse, parse_qs, urlencode

    parsed_url = urlparse(url)
    query = parse_qs(parsed_url.query)
    param = next(iter(query.pop(name, list())), None)
    url = parsed_url._replace(query=urlencode(query, True)).geturl()
    return (url, param)

def verify_signed_url(key, signed_url):
    unsigned_url, encoded_signature = pop_query_parameter(signed_url, "signature")
    received_signature = base64.urlsafe_b64decode(encoded_signature)
    computed_signature = compute_signature(key, unsigned_url)
    
    passes = hmac.compare_digest(computed_signature, received_signature)
    if not passes:
        sanitised_url, _ = pop_query_parameter(unsigned_url, "custom_data")
        logging.warning(
            f"Signature mismatch.\n"
            f"    URL (custom data omitted): {sanitised_url}\n"
            f"    Received: {received_signature}\n"
            f"    Computed: {computed_signature}"
        )

    return passes

def compute_signature(key, unsigned_url):
    return hmac.new(
        key,
        bytes(unsigned_url, encoding='utf-8'),
        digestmod=hashlib.sha256
    ).digest()


