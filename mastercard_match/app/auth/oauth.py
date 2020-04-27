from OpenSSL import crypto
from random import randint
import json

from .utils import uri_rfc3986_encode, base64_encode, sha256_encode, normalize_url, normalize_params

from urllib import parse
from urllib.parse import urlencode
from schematics import Model
from collections.abc import Mapping
import time
import uuid


def load_signing_key(cert):
    """
        Load passwordless pem certificate
    """
    private_key = crypto.load_privatekey(crypto.FILETYPE_PEM, cert)

    return private_key


class OAuth(object):
    def __init__(self, pem_cert, consumer_key):
        self.private_key = load_signing_key(pem_cert)
        self.consumer_key = consumer_key

    def get_authorization_header(self, uri, method, payload, params=None):
        # need to add query parameters as they
        # will used in generating the signature
        if params:
            uri = uri + "?" + urlencode(params)
        oauth_parameters = self.get_oauth_parameters(uri, method, payload)

        # Generate the header value for OAuth Header
        oauth_key = 'OAuth' + ' ' + ','.join([
            uri_rfc3986_encode(str(k)) + '=\"' + uri_rfc3986_encode(str(v)) + '\"'
            for k, v in oauth_parameters.items()]
        )

        return oauth_key

    def get_oauth_parameters(self, uri, method, payload):
        oauth_parameters = OAuthParameters()
        oauth_parameters['oauth_consumer_key'] = self.consumer_key

        payload_str = json.dumps(payload) if payload else ''

        oauth_parameters['oauth_body_hash'] = base64_encode(sha256_encode(payload_str))

        base_string = self.get_base_string(uri, method, oauth_parameters)
        oauth_parameters['oauth_signature'] = self.sign_message(base_string)

        return oauth_parameters

    def get_base_string(self, url, method, oauth_parameters):
        merge_dict = oauth_parameters.mapping.copy()
        return "{}&{}&{}".format(uri_rfc3986_encode(method.upper()),
                                 uri_rfc3986_encode(normalize_url(url)),
                                 uri_rfc3986_encode(normalize_params(url, merge_dict)))

    def sign_message(self, message):
        sign = crypto.sign(self.private_key, message.encode("utf-8"), 'SHA256')
        return base64_encode(sign)


class OAuthParameters(Mapping):
    """
    Stores the OAuth parameters required to generate the Base String and Headers constants
    """

    def __init__(self):
        mapping = {}
        mapping['oauth_signature_method'] = 'RSA-SHA256'
        mapping['oauth_version'] = '1.0'
        mapping['oauth_nonce'] = str(uuid.uuid4().hex + uuid.uuid1().hex)[:16]
        mapping['oauth_timestamp'] = int(time.time())

        self.mapping = mapping

    def __getitem__(self, key):
        return self.mapping[key]

    def __delitem__(self, key):
        del self.mapping[key]

    def __setitem__(self, key, value):
        self.mapping[key] = value

    def __iter__(self):
        return iter(self.mapping)

    def __len__(self):
        return len(self.mapping)
