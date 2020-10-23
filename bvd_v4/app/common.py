import logging


# Deterministically creates associate UUID from string
def build_resolver_id(original_id):
    from uuid import NAMESPACE_X500, uuid3

    if not original_id:
        logging.error({"message": "Invalid associate ID", "original_id": original_id})

    return uuid3(NAMESPACE_X500, original_id)
