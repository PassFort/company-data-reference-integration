# This file is mocked out for testing (see `tests/conftest.py`)

import base64
import logging
import os
import sys


def _env(name):
    try:
        return os.environ[name]
    except KeyError:
        sys.exit(f"Missing required environment variable: {name}")


INTEGRATION_SECRET_KEY = _env("INTEGRATION_SECRET_KEY")

integration_key_store = {
    INTEGRATION_SECRET_KEY[:8]: base64.b64decode(INTEGRATION_SECRET_KEY)
}

logging.basicConfig(level=os.environ.get("LOGLEVEL", "INFO"))
