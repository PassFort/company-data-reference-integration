from app.http_signature import HTTPSignatureAuth
from app.startup import integration_key_store

auth = HTTPSignatureAuth()


@auth.resolve_key
def resolve_key(key_id):
    return integration_key_store.get(key_id)
