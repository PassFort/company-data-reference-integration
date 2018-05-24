from freezegun import freeze_time
from unittest import TestCase

from app.auth import CustomAuthApiClient
from swagger_client.models import NewCase, ProviderType, CaseEntityType


@freeze_time('2018-05-23 14:34:12')
class TestCustomAuthApiClient(TestCase):

    def test_computes_headers(self):
        client = CustomAuthApiClient(
            'rms-world-check-one-api-pilot.thomsonreuters.com',
            'a4364e62-e58b-4b64-9c71-faead5417557',
            '/NoVqWHBRv23t5ae9OuQlODUX5yoAcJcFP8Z2nJldBkrsTCdqhRzGzrrTvD9EVqLgwTrXC4xKZ/Khfv6shMwAA==')

        with self.subTest('for get'):
            self.assertDictEqual(
                client.generate_headers('/references/countries', 'GET', None),
                {
                    'Date': 'Wed, 23 May 2018 14:34:12 GMT',
                    'Authorization': 'Signature keyId="a4364e62-e58b-4b64-9c71-faead5417557",'
                                     'algorithm="hmac-sha256",'
                                     'headers="(request-target) host date",'
                                     'signature="5RrUrWrX+X9oUi2sNx+Xir80Q/+FyTeWNkYQ9iyxp+U="'
                })

        with self.subTest('for post with body'):
            self.assertDictEqual(
                client.generate_headers('/cases', 'POST', NewCase(
                    name="Putin",
                    provider_types=[ProviderType.WATCHLIST],
                    entity_type=CaseEntityType.INDIVIDUAL,
                    group_id="418f28a7-b9c9-4ae4-8530-819c61b1ca6c")),
                {
                    'Date': 'Wed, 23 May 2018 14:34:12 GMT',
                    'Authorization': 'Signature keyId="a4364e62-e58b-4b64-9c71-faead5417557",'
                                     'algorithm="hmac-sha256",'
                                     'headers="(request-target) host date content-type content-length",'
                                     'signature="jbPbNK7qqgmFx/kkaqwlyPlPjDRjCitMy/ANBCfjHZA="'
                })