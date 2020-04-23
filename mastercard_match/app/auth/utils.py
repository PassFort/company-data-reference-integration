from urllib.parse import urlparse, quote, parse_qsl, urlencode
import base64
import hashlib
import uuid
import time


def uri_rfc3986_encode(value):
    return quote(value, safe='%')


def sha256_encode(value):
    return hashlib.sha256(str(value).encode('utf-8')).digest()


def base64_encode(text):
    encode = base64.b64encode(text)
    if isinstance(encode, (bytearray, bytes)):
        return encode.decode('ascii')
    else:
        return encode


def normalize_url(url):
    parsed = urlparse(url)
    return "{}://{}{}".format(parsed.scheme, parsed.netloc.lower(), parsed.path)


def encode_pair(key, value):
    encoded_key = oauth_query_string_element_encode(key)
    encoded_value = oauth_query_string_element_encode(value if isinstance(value, bytes) else str(value))
    return "%s=%s" % (encoded_key, encoded_value)


def normalize_params(url, params={}):
    parse = urlparse(url)
    qs_list = parse_qsl(parse.query, keep_blank_values=True)
    qs_list += params.items()
    encoded_list = [encode_pair(k, v) for k, v in qs_list]
    sorted_list = sorted(encoded_list, key=lambda x: x)

    return '&'.join(sorted_list)


def oauth_query_string_element_encode(value):
    return quote(value)
