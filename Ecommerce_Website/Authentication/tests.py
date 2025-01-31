from django.test import TestCase, Client
from django.urls import reverse
from unittest.mock import patch

class GoogleAuthTest(TestCase):
    def setUp(self):
        self.client = Client()
        
    @patch('social_core.backends.google.GoogleOAuth2.do_auth')
    def test_google_login(self, mock_do_auth):
        # Mock the Google OAuth2 response
        mock_do_auth.return_value = {
            'email': 'test@gmail.com',
            'given_name': 'Test',
            'family_name': 'User',
            'picture': 'http://example.com/picture.jpg'
        }
        
        response = self.client.get(
            reverse('social:complete', kwargs={'backend': 'google-oauth2'})
        )
        self.assertEqual(response.status_code, 302)
