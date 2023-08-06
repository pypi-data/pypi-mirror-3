
from django.test import TestCase, RequestFactory
from django.contrib.auth.models import User, AnonymousUser
from django.core.exceptions import ImproperlyConfigured
from django.core.cache import cache
from django.contrib.sessions.middleware import SessionMiddleware
from django.core.urlresolvers import reverse

import utils
import settings
import middleware
import auth
from templatetags.openonmobile_tags import openonmobile_img, \
                                            openonmobile_image_url


class CreateKeyTest(TestCase):

    def test_create_key_default_length(self):
        key = utils.create_random_auth_key()

        self.assertEqual(len(key), settings.OPENONMOBILE_KEY_LENGTH)

    def test_create_key_fixed_length(self):
        key = utils.create_random_auth_key(25)

        self.assertEqual(len(key), 25)

    def test_create_key_chars(self):
        key = utils.create_random_auth_key()

        self.assertTrue(all(c in utils.key_chars for c in key))


class MobileUrlTest(TestCase):

    request_factory = RequestFactory()

    def test_url_default(self):

        request = self.request_factory.get('/hello/')
        request.user = AnonymousUser()
        url = utils.mobile_url(request)
        self.assertEqual(url, 'http://testserver/')

    def test_url_with_get(self):

        request = self.request_factory.get('/hello/', {'url': '/bye'})
        request.user = AnonymousUser()
        url = utils.mobile_url(request)
        self.assertEqual(url, 'http://testserver/bye')

    def test_url_with_auth(self):

        request = self.request_factory.get('/hello/')
        request.user = User(username='testuser')
        url = utils.mobile_url(request)
        expected = '?%s=' % settings.OPENONMOBILE_KEY
        self.assertTrue(expected in url)


class MiddlewareTest(TestCase):

    request_factory = RequestFactory()
    middleware = middleware.AuthOnMobileMiddleware()

    def test_default(self):

        request = self.request_factory.get('/hello/')
        request.user = AnonymousUser()

        res = self.middleware.process_request(request)

        self.assertEqual(res, None)
        self.assertFalse(request.user.is_authenticated())

    def test_not_configured(self):

        request = self.request_factory.get('/hello/')

        self.assertRaises(ImproperlyConfigured,
                self.middleware.process_request, request)

    def test_authenticated(self):

        request = self.request_factory.get('/hello/')
        request.user = User(username='testuser')

        res = self.middleware.process_request(request)

        self.assertEqual(res, None)
        self.assertTrue(request.user.is_authenticated())

    def test_invalid_key(self):

        data = {settings.OPENONMOBILE_KEY: 'invalid'}
        request = self.request_factory.get('/hello/', data)
        request.user = AnonymousUser()

        res = self.middleware.process_request(request)

        self.assertEqual(res, None)
        self.assertFalse(request.user.is_authenticated())

    def test_valid_key(self):
        secret = 'valid_key_secret'
        user = User(username='testuser')
        user.save()
        cache.set(secret, user.id)

        data = {settings.OPENONMOBILE_KEY: secret}
        request = self.request_factory.get('/hello/', data)
        request.user = AnonymousUser()
        SessionMiddleware().process_request(request)

        res = self.middleware.process_request(request)

        self.assertEqual(res, None)
        self.assertTrue(request.user.is_authenticated())


class AuthTest(TestCase):

    backend = auth.AuthOnMobileBackend()

    def test_authenticate(self):
        secret = 'valid_key_secret'
        user = User(username='testuser')
        user.save()
        cache.set(secret, user.id)

        auth_user = self.backend.authenticate(openonmobile=secret)

        self.assertEqual(user, auth_user)

    def test_not_key(self):
        user = self.backend.authenticate()

        self.assertEqual(user, None)

    def test_invalid_user(self):
        secret = 'valid_key_secret'
        user = self.backend.authenticate(openonmobile=secret)

        self.assertEqual(user, None)

    def test_get_user(self):
        user = User(username='testuser')
        user.save()
        got_user = self.backend.get_user(user.id)

        self.assertEqual(user, got_user)

    def test_get_user_invalid(self):
        got_user = self.backend.get_user(0)

        self.assertEqual(got_user, None)


class TemplateTagsTest(TestCase):

    request_factory = RequestFactory()

    def test_img_tag(self):
        request = self.request_factory.get('/hello/')
        request.user = AnonymousUser()
        context = {
            'request': request
        }
        tag = openonmobile_img(context)

        self.assertEqual(tag, '<img src="/qr/?url=/hello/">')

    def test_img_tag_rotate(self):
        request = self.request_factory.get('/hello/')
        request.user = AnonymousUser()
        context = {
            'request': request
        }
        tag = openonmobile_img(context, rotate=45)

        self.assertEqual(tag, '<img src="/qr/?url=/hello/&rotate=45">')

    def test_img_tag_width(self):
        request = self.request_factory.get('/hello/')
        request.user = AnonymousUser()
        context = {
            'request': request
        }
        tag = openonmobile_img(context, width='200px')

        self.assertEqual(tag, '<img src="/qr/?url=/hello/" width="200px">')

    def test_image_url(self):
        request = self.request_factory.get('/hello/')
        request.user = AnonymousUser()
        context = {
            'request': request
        }
        tag = openonmobile_image_url(context)

        self.assertEqual(tag, '/qr/?url=/hello/')

    def test_image_url_rotate(self):
        request = self.request_factory.get('/hello/')
        request.user = AnonymousUser()
        context = {
            'request': request
        }
        tag = openonmobile_image_url(context,  rotate=45)

        self.assertEqual(tag, '/qr/?url=/hello/&rotate=45')


class ViewTest(TestCase):

    def test_qr(self):
        response = self.client.get(reverse('openonmobile_qr'))
        self.assertEqual(response.status_code, 200)

    def test_qr_rotate(self):
        response = self.client.get(reverse('openonmobile_qr'), {'rotate': 45})
        self.assertEqual(response.status_code, 200)

    def test_qr_content_type(self):
        response = self.client.get(reverse('openonmobile_qr'))
        self.assertEqual(response['content-type'], 'image/png')
