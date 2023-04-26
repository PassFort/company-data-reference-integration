import base64

INTEGRATION_SECRET_KEY = "dummykey" 

dummy_key = base64.b64decode(INTEGRATION_SECRET_KEY) + bytes(250)

integration_key_store = {"dummykey": dummy_key}
