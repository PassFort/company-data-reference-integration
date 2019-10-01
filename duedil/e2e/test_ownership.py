import unittest
import requests

API_URL = 'http://localhost:8001'

CREDENTIALS = {
    "auth_token": "f1137e75bf253e6eb4231a9a09b5a76d"
}

GLOBAL_COVERAGE = {
    "has_global_coverage": True
}


# class OwnershipTests(unittest.TestCase):

#     def test_passfort_gbr(self):
#         response = requests.post(API_URL + '/ownership-check', json={
#             "input_data": {
#                 "metadata": {
#                     "country_of_incorporation": {
#                         "v": "GBR"
#                     },
#                     "number": {
#                         "v": "09565115"
#                     }
#                 }
#             },
#             "config": {},
#             "credentials": CREDENTIALS,
#         })
#         result = response.json()

#         shareholders = result['output_data']['ownership_structure']['shareholders']
#         henry = [s for s in shareholders if s.get('dob', {}).get('v') == '1991-08'][0]

#         self.assertEqual(response.status_code, 200)
#         self.assertEqual(henry['last_name']['v'], 'Irish')
#         self.assertTrue(len(shareholders) >= 10)

#     def test_boylesports_irl(self):
#         response = requests.post(API_URL + '/ownership-check', json={
#             "input_data": {
#                 "metadata": {
#                     "country_of_incorporation": {
#                         "v": "IRL"
#                     },
#                     "number": {
#                         "v": "194670"
#                     }
#                 }
#             },
#             "config": {},
#             "credentials": CREDENTIALS,
#         })
#         result = response.json()

#         shareholders = result['output_data']['ownership_structure']['shareholders']

#         self.assertEqual(response.status_code, 200)
#         self.assertTrue(len(shareholders) >= 1)

#     def test_bad_company_number(self):
#         response = requests.post(API_URL + '/ownership-check', json={
#             "input_data": {
#                 "metadata": {
#                     "country_of_incorporation": {
#                         "v": "GBR"
#                     },
#                     "number": {
#                         "v": "57209aa920"
#                     }
#                 }
#             },
#             "config": {},
#             "credentials": CREDENTIALS,
#         })
#         result = response.json()
#         self.assertEqual(response.status_code, 200)
#         self.assertIs(result.get('output_data', None), None)
#         self.assertIs(result.get('raw', None), None)

#     def test_no_global_coverage(self):
#         response = requests.post(API_URL + '/ownership-check', json={
#             "input_data": {
#                 "metadata": {
#                     "country_of_incorporation": {
#                         "v": "FRA"
#                     },
#                     "number": {
#                         "v": "572093920"
#                     }
#                 }
#             },
#             "config": {},
#             "credentials": CREDENTIALS,
#         })
#         result = response.json()
#         self.assertEqual(response.status_code, 200)
#         self.assertEqual(
#             result['errors'][0]['message'],
#             'Country \'FRA\' is not supported by the provider for this stage'
#         )

#     def test_with_global_coverage(self):
#         response = requests.post(API_URL + '/ownership-check', json={
#             "input_data": {
#                 "metadata": {
#                     "country_of_incorporation": {
#                         "v": "FRA"
#                     },
#                     "number": {
#                         "v": "572093920"
#                     }
#                 }
#             },
#             "config": GLOBAL_COVERAGE,
#             "credentials": CREDENTIALS,
#         })
#         result = response.json()
#         self.assertEqual(response.status_code, 200)
#         self.assertEqual(len(result['errors']), 0)
