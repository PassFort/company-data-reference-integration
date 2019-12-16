from typing import Tuple, Union
from tempfile import mkdtemp, mkstemp
from os import path, remove, getcwd, chdir
from contextlib import contextmanager
from zeep import Client
from zeep.transports import Transport
from requests import Session
from requests.exceptions import HTTPError
from passfort.cifas_search import CifasCredentials, CifasConfig
from cifas.search import FullSearchRequest, FullSearchResponse
from cifas.soap_header import StandardHeader


WSDL_DIR = path.join(path.dirname(__file__), 'schema')
WSDL_FILENAME = 'DirectServiceCIFAS.wsdl'
CIFAS_SCHEMA_VERSION = '3-00'
PASSFORT_CURRENT_USER = 'PassfortUser1105'
PASSFORT_MEMBER_ID = 1106
TRAINING_WSDL_FILENAME = 'TrainingDirectServiceCIFAS.wsdl'
CERTS_DIRECTORY = mkdtemp(prefix='cifas-certs-')


class CifasConnectionError(Exception):
    pass


class CifasHTTPError(Exception):
    pass


@contextmanager
def change_cwd(cwd: str):
    # This changes the current directory
    # and restores it back to normal afterwards...
    original_cwd = getcwd()
    chdir(cwd)
    yield cwd
    chdir(original_cwd)


@contextmanager
def request_ctx():
    try:
        yield
    except ConnectionError as e:
        raise CifasConnectionError(e)
    except HTTPError as e:
        raise CifasHTTPError(e)


def create_soap_client(cert_file: str, wsdl_path: str) -> Client:
    session = Session()
    session.cert = cert_file

    with change_cwd(WSDL_DIR), request_ctx():
        soap_client = Client(wsdl_path, transport=Transport(session=session))

    soap_client.set_ns_prefix('fh', 'http://header.find-cifas.org.uk')
    soap_client.set_ns_prefix('doc', 'http://objects.find-cifas.org.uk/Direct')
    return soap_client


def create_cert_file(credentials: CifasCredentials) -> str:
    _, cert_file = mkstemp(dir=CERTS_DIRECTORY)
    with open(cert_file, 'w') as file:
        file.write(credentials.cert)
    return cert_file


class CifasAPIClient:
    def __init__(self, config: CifasConfig, credentials: CifasCredentials):
        self.config = config
        self.cert_file = create_cert_file(credentials)
        self.soap_client = create_soap_client(self.cert_file, self.wsdl_path)

    @property
    def wsdl_path(self):
        if self.config.use_uat:
            return TRAINING_WSDL_FILENAME
        return WSDL_FILENAME

    def destroy(self):
        remove(self.cert_file)

    def get_header(self, requesting_institution: int) -> StandardHeader:
        return StandardHeader(
            RequestingInstitution=requesting_institution,
            OwningMemberNumber=PASSFORT_MEMBER_ID,
            ManagingMemberNumber=PASSFORT_MEMBER_ID,
            CurrentUser=PASSFORT_CURRENT_USER,
            SchemaVersion=CIFAS_SCHEMA_VERSION,
        )

    def full_search(self, request: FullSearchRequest) -> FullSearchResponse:
        with request_ctx():
            response_object = self.soap_client.service.FullSearch(
                _soapheaders=[self.get_header(self.config.requesting_institution)],
                Search=request.to_dict(),
            )

        return FullSearchResponse.from_dict(response_object.__values__)
