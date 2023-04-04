import base64
from dataclasses import dataclass
from uuid import UUID

from hypothesis import given, assume
import hypothesis.strategies as st

from app.api.signed_url import verify_signed_url, compute_signature
from tests.url_strategy import SecretKey, Url

# 32 random bytes encoded as standard base64
VALID_KEY = base64.b64decode("h/BTMtonCqWQggdfEv47tMEFbc1RwRdqCnbHSRvk5WU=")

def assert_valid(key, url, signature):
    assert(verify_signed_url(key, f"{url}&signature={signature}"))

@given(SecretKey, SecretKey, Url)
def test_different_keys_produce_different_signatures(key_a, key_b, url):
    assume(key_a != key_b)
    assert compute_signature(key_a, str(url)) != compute_signature(key_b, str(url))

@given(SecretKey, Url)
def test_identical_keys_produce_identical_signatures(key, url):
    assert compute_signature(key, str(url)) == compute_signature(key, str(url))

def test_valid_with_basic_custom_data():
    url = "http://example.com/some-path?custom_data=some-custom-data&version=1&valid_until=123456789&auditee_id=C800B3EB-5960-4D84-9F96-129C2F4EE214"
    signature="JpqyXrjQ-yaEa8VufDGjcf5rR4R-FSPX1b6RArf89EA%3D"
     
    assert_valid(VALID_KEY, url, signature)

def test_valid_without_custom_data():
    url = "http://example.com/some-path?version=1&valid_until=123456789&auditee_id=C800B3EB-5960-4D84-9F96-129C2F4EE214"
    signature = "DgSiCzFTCJaFiR_hNbB3w_PVtyD6SSNBk8YPMUdApNc%3D"
    assert_valid(VALID_KEY, url, signature)


