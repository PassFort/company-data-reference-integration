import logging

from tempfile import mkdtemp, mkstemp
from os import path, remove, environ
from contextlib import contextmanager
from lxml import etree
from zeep import Client
from zeep.transports import Transport
from zeep.helpers import serialize_object
from zeep.exceptions import Fault
from zeep.plugins import HistoryPlugin
from requests import Session
from requests.exceptions import HTTPError, ConnectionError
from passfort.cifas_check import CifasCredentials, CifasConfig
from passfort.error import CifasConnectionError, CifasHTTPError
from cifas.search import FullSearchRequest, FullSearchResponse
from cifas.soap_header import StandardHeader


WSDL_DIR = path.join(path.dirname(__file__), 'schema')
WSDL_FILENAME = 'cifas/schema/DirectServiceCIFAS.wsdl'
CIFAS_SCHEMA_VERSION = '3-00'
PASSFORT_MEMBER_ID = 1070
PASSFORT_TRAINING_MEMBER_ID = 1105
TRAINING_WSDL_FILENAME = 'cifas/schema/TrainingDirectServiceCIFAS.wsdl'
CERTS_DIRECTORY = mkdtemp(prefix='cifas-certs-')


logger = logging.getLogger('cifas')
logger.setLevel(logging.INFO)


@contextmanager
def request_ctx(client):
    try:
        yield
    except ConnectionError as e:
        raise CifasConnectionError(e)
    except HTTPError as e:
        raise CifasHTTPError(e)
    except Fault as e:
        logger.error({
            'message': 'soap_fault',
            'soap_fault_detail': client.wsdl.types.deserialize(e.detail[0])
        })
        raise e


def create_soap_client(cert_file: str, wsdl_path: str) -> Client:
    session = Session()
    session.cert = cert_file

    soap_client = Client(wsdl_path, transport=Transport(session=session))
    soap_client.set_ns_prefix('fh', 'http://header.find-cifas.org.uk')
    soap_client.set_ns_prefix('doc', 'http://objects.find-cifas.org.uk/Direct')

    if environ.get('CIFAS_HTTPS_PROXY'):
        soap_client.transport.session.proxies = {
            'https': environ.get('CIFAS_HTTPS_PROXY'),
        }
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
        self.history = HistoryPlugin()
        self.soap_client = create_soap_client(self.cert_file, self.wsdl_path)

    @property
    def wsdl_path(self):
        if self.config.use_uat:
            return TRAINING_WSDL_FILENAME
        return WSDL_FILENAME

    def destroy(self):
        remove(self.cert_file)

    def get_header(self, member_id: int) -> StandardHeader:
        return StandardHeader(
            RequestingInstitution=(
                PASSFORT_TRAINING_MEMBER_ID if self.config.use_uat else PASSFORT_MEMBER_ID
            ),
            OwningMemberNumber=member_id,
            ManagingMemberNumber=member_id,
            CurrentUser=self.config.user_name,
            SchemaVersion=CIFAS_SCHEMA_VERSION,
        )

    def full_search(self, request: FullSearchRequest) -> FullSearchResponse:
        with request_ctx(self.soap_client):
            response_object = self.soap_client.service.FullSearch(
                _soapheaders=[self.get_header(self.config.member_id)],
                Search=request.to_dict(),
            )

        self.log_last_request()
        return FullSearchResponse.from_dict(serialize_object(response_object))

    def log_last_request(self):
        history = self.history
        try:
            logger.info({
                'message': 'cifas_check_xml',
            }, **{
                f'cifas_check_{msg_type}': etree.tostring(msg['envelop'], encoding='unicode', pretty_print=True)
                for msg_type, msg in (
                    ('request', history.last_sent),
                    ('response', history.last_received),
                )
            })
        except (IndexError, TypeError):
            logger.error({'message': 'cifas_logging_exception'})
            pass
