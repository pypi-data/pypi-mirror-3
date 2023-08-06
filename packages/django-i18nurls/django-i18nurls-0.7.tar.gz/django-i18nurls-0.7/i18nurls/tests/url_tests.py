from django.core.urlresolvers import reverse
from django.utils.translation import activate

from i18nurls.tests.base import BaseTestCase


class PrefixTest(BaseTestCase):

    def test_not_prefixed_url(self):
        activate('en')
        self.assertEqual(reverse('not-prefixed'), '/not-prefixed/')
        activate('nl')
        self.assertEqual(reverse('not-prefixed'), '/not-prefixed/')

    def test_prefixed_url(self):
        activate('en')
        self.assertEqual(reverse('prefixed'), '/en/prefixed/')
        activate('nl')
        self.assertEqual(reverse('prefixed'), '/nl/prefixed/')


class TranslationTest(BaseTestCase):

    def test_url(self):
        activate('en')
        self.assertEqual(reverse('news'), '/en/news/')
        activate('nl')
        self.assertEqual(reverse('news'), '/nl/nieuws/')


class NamespaceTest(BaseTestCase):

    def test_namespace(self):
        activate('en')
        self.assertEqual(reverse('users:register'), '/en/users/register/')
        activate('nl')
        self.assertEqual(
            reverse('users:register'), '/nl/gebruikers/registeren/')


class RedirectTest(BaseTestCase):

    def test_trailing_slash_redirect_en(self):
        response = self.client.get('/en', HTTP_ACCEPT_LANGUAGE='nl')
        self.assertEqual(response.status_code, 301)
        self.assertEqual(response.has_header('location'), True)
        self.assertEqual(
            response['location'], 'http://testserver/en/')

    def test_trailing_slash_redirect_nl(self):
        response = self.client.get('/nl', HTTP_ACCEPT_LANGUAGE='en')
        self.assertEqual(response.status_code, 301)
        self.assertEqual(response.has_header('location'), True)
        self.assertEqual(
            response['location'], 'http://testserver/nl/')

    def test_en_redirect(self):
        response = self.client.get(
            '/users/register/', HTTP_ACCEPT_LANGUAGE='en')
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.has_header('location'), True)
        self.assertEqual(
            response['location'], 'http://testserver/en/users/register/')

        response = self.client.get(response['location'])
        self.assertEqual(response.status_code, 200)

    def test_en_redirect_wrong_url(self):
        response = self.client.get(
            '/gebruikers/registeren/', HTTP_ACCEPT_LANGUAGE='en')
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.has_header('location'), True)
        self.assertEqual(
            response['location'],
            'http://testserver/en/gebruikers/registeren/'
        )

        response = self.client.get(response['location'])
        self.assertEqual(response.status_code, 404)

    def test_nl_redirects(self):
        response = self.client.get(
            '/gebruikers/registeren/', HTTP_ACCEPT_LANGUAGE='nl')
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.has_header('location'), True)
        self.assertEqual(
            response['location'],
            'http://testserver/nl/gebruikers/registeren/'
        )

        response = self.client.get(response['location'])
        self.assertEqual(response.status_code, 200)

    def test_nl_redirects_wrong_url(self):
        response = self.client.get(
            '/users/register/', HTTP_ACCEPT_LANGUAGE='nl')
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.has_header('location'), True)
        self.assertEqual(
            response['location'], 'http://testserver/nl/users/register/')

        response = self.client.get(response['location'])
        self.assertEqual(response.status_code, 404)


class ResponseTest(BaseTestCase):

    def test_en_url(self):
        response = self.client.get('/en/users/register/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['content-language'], 'en')
        self.assertEqual(response.context['LANGUAGE_CODE'], 'en')

    def test_nl_url(self):
        response = self.client.get('/nl/gebruikers/registeren/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['content-language'], 'nl')
        self.assertEqual(response.context['LANGUAGE_CODE'], 'nl')

    def test_wrong_en_prefix(self):
        response = self.client.get('/en/gebruikers/registeren/')
        self.assertEqual(response.status_code, 404)

    def test_wrong_nl_prefix(self):
        response = self.client.get('/nl/users/register/')
        self.assertEqual(response.status_code, 404)
