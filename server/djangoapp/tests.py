import json
from unittest.mock import patch

from django.contrib.auth import get_user
from django.test import Client, TestCase
from requests.exceptions import ConnectionError


class AuthenticationTests(TestCase):
    def test_register_login_logout_session(self):
        payload = {'userName': 'testdriver', 'password': 'test-password',
                   'email': 'driver@example.com', 'firstName': 'Test',
                   'lastName': 'Driver'}
        response = self.client.post('/djangoapp/register', data=json.dumps(
            payload), content_type='application/json')
        self.assertEqual(response.json()['status'], 'Authenticated')
        self.assertTrue(get_user(self.client).is_authenticated)
        self.client.get('/djangoapp/logout')
        self.assertFalse(get_user(self.client).is_authenticated)
        response = self.client.post('/djangoapp/login', data=json.dumps(
            payload), content_type='application/json')
        self.assertEqual(response.json()['status'], 'Authenticated')


class ProxyTests(TestCase):
    @patch('djangoapp.views.get_request')
    def test_state_filter(self, upstream):
        upstream.return_value = [{'id': 1, 'state': 'Kansas'}]
        response = self.client.get('/djangoapp/get_dealers/Kansas')
        upstream.assert_called_once_with('/fetchDealers/Kansas')
        self.assertEqual(response.json()['dealers'][0]['state'], 'Kansas')

    @patch('djangoapp.views.analyze_review_sentiments')
    @patch('djangoapp.views.get_request')
    def test_review_sentiment(self, upstream, analyze):
        upstream.return_value = [{'id': 1, 'review': 'Fantastic services'}]
        analyze.return_value = {'sentiment': 'positive'}
        response = self.client.get('/djangoapp/reviews/dealer/1')
        self.assertEqual(response.json()['reviews'][0]['sentiment'], 'positive')

    @patch('djangoapp.views.get_request', side_effect=ConnectionError)
    def test_unavailable_service_reports_failure(self, upstream):
        self.assertEqual(self.client.get('/djangoapp/get_dealers').status_code,
                         502)

    def test_anonymous_review_is_rejected(self):
        response = Client().post('/djangoapp/add_review', data='{}',
                                 content_type='application/json')
        self.assertEqual(response.status_code, 403)
