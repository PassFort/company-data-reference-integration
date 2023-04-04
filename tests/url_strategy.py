from dataclasses import dataclass
import string 
from uuid import UUID

import hypothesis.strategies as st

from app.auth.signed_urls import verify_signed_url, compute_signature

# Minimal strategy for generating example URLs 
# Does not account for or include many valid URLs 
# For example ports, fragments and query params are never added

URL_PROTOCOLS = ["http", "https"]

def domain_labels():
    return st.from_regex("[A-Za-z0-9][A-Za-z0-9-]*[A-Za-z0-9]|[A-Za-z0-9]", fullmatch=True)

def top_labels():
    return st.from_regex("[A-Za-z][A-Za-z0-9-]*[A-Za-z0-9]|[A-Za-z]", fullmatch=True)

def host_names():
    return st.builds(
        "{}.{}".format,
        st.lists(domain_labels(), min_size=1).map(".".join),
        top_labels()
    )

def paths():
    return st.lists(st.from_regex("[A-Za-z0-9-_.$.+]+", fullmatch=True)).map("/".join)

def urls():
    return st.builds(
        "{}://{}/{}".format,
        st.sampled_from(URL_PROTOCOLS),
        host_names(),
        paths()
    )


@dataclass
class SignedUrl:
    base_url: str

    version: int
    valid_until: int
    auditee_id: UUID
    custom_data: str = None

    def __str__(self):
        if self.custom_data:
            return f"{self.base_url}?custom_data={self.custom_data}&version={self.version}&valid_until={self.valid_until}&auditee_id={self.auditee_id}"
        else:
            return f"{self.base_url}?version={self.version}&valid_until={self.valid_until}&auditee_id={self.auditee_id}"


AuditeeId = st.uuids(allow_nil=True)
SecretKey = st.binary(min_size=32, max_size=32)
Timestamp = st.integers(min_value=0, max_value=2**32 - 1)
Version = st.integers(min_value=1, max_value=1)

Url = st.builds(
    SignedUrl,
    urls(),
    Version,
    Timestamp,
)
