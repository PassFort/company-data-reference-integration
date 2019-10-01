import unittest
import requests

API_URL = 'http://localhost:8001'

CREDENTIALS = {
    "auth_token": "f1137e75bf253e6eb4231a9a09b5a76d"
}

GLOBAL_COVERAGE = {
    "has_global_coverage": True
}


# class CharitiesTests(unittest.TestCase):

#     def test_macmillan_gbr(self):
#         response = requests.post(API_URL + '/charity-check', json={
#             "input_data": {
#                 "metadata": {
#                     "country_of_incorporation": "GBR",
#                     "number": "09565115",
#                     "name": "Macmillan Cancer Support",
#                 }
#             },
#             "config": {},
#             "credentials": CREDENTIALS,
#         })
#         result = response.json()

#         trustees = result['output_data']['officers']['trustees']

#         self.assertEqual(response.status_code, 200)
#         self.assertTrue(len(trustees) >= 10)
#         self.assertEqual(result['output_data']['metadata']['uk_charity_commission_number'], '261017')

#     def test_freeman_gbr(self):
#         response = requests.post(API_URL + '/charity-check', json={
#             "input_data": {
#                 "metadata": {
#                     "country_of_incorporation": "GBR",
#                     "number": "CE002298",
#                     "name": "FREEMAN HEART & LUNG TRANSPLANT ASSOCIATION",
#                 }
#             },
#             "config": {},
#             "credentials": CREDENTIALS,
#         })
#         result = response.json()

#         trustees = result['output_data']['officers']['trustees']

#         self.assertEqual(response.status_code, 200)
#         self.assertEqual(result['output_data']['metadata']['uk_charity_commission_number'], '1157894')
#         self.assertTrue(len(trustees) > 5)


# class CharitiesErrorHandlingTests(unittest.TestCase):

#     def test_missing_name(self):
#         response = requests.post(API_URL + '/charity-check', json={
#             "input_data": {
#                 "metadata": {
#                     "country_of_incorporation": "GBR",
#                     "number": "CE002298",
#                 }
#             },
#             "config": {},
#             "credentials": CREDENTIALS,
#         })
#         result = response.json()

#         self.assertEqual(response.status_code, 200)
#         self.assertEqual(result['errors'][0]['message'], 'Missing company name in input')
#         self.assertEqual(len(result['errors']), 1)

#     def test_missing_country(self):
#         response = requests.post(API_URL + '/charity-check', json={
#             "input_data": {
#                 "metadata": {
#                     "number": "CE002298",
#                     "name": "FREEMAN HEART & LUNG TRANSPLANT ASSOCIATION",
#                 }
#             },
#             "config": {},
#             "credentials": CREDENTIALS,
#         })
#         result = response.json()

#         self.assertEqual(response.status_code, 200)
#         self.assertEqual(result['errors'][0]['message'], 'Missing country in input')
#         self.assertEqual(len(result['errors']), 1)

#     def test_missing_number(self):
#         response = requests.post(API_URL + '/charity-check', json={
#             "input_data": {
#                 "metadata": {
#                     "country_of_incorporation": "GBR",
#                     "name": "FREEMAN HEART & LUNG TRANSPLANT ASSOCIATION",
#                 }
#             },
#             "config": {},
#             "credentials": CREDENTIALS,
#         })
#         result = response.json()

#         self.assertEqual(response.status_code, 200)
#         self.assertEqual(result['errors'][0]['message'], 'Missing company number in input')
#         self.assertEqual(len(result['errors']), 1)

#     def test_multiple_missing(self):
#         response = requests.post(API_URL + '/charity-check', json={
#             "input_data": {
#                 "metadata": {
#                     "country_of_incorporation": "GBR",
#                 }
#             },
#             "config": {},
#             "credentials": CREDENTIALS,
#         })
#         result = response.json()

#         self.assertEqual(response.status_code, 200)
#         self.assertEqual(len(result['errors']), 2)
#         self.assertEqual(result['errors'][0]['message'], 'Missing company number in input')
#         self.assertEqual(result['errors'][1]['message'], 'Missing company name in input')
