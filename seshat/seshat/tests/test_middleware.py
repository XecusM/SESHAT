from django.contrib.auth.models import AnonymousUser
from django.http import HttpResponse, HttpResponseNotAllowed
from django.test import RequestFactory, TestCase, override_settings

from seshat import middleware
from seshat.testing import create_user


class ContextProcessorsTest(TestCase):
    '''
    Test the debug and theme context processors
    '''

    def setUp(self):
        self.request = RequestFactory().get('/')

    @override_settings(DEBUG=True)
    def test_debug(self):
        self.assertEqual(middleware.debug(self.request), {'DEBUG': True})

    def test_theme_anonymous(self):
        self.request.user = AnonymousUser()
        self.assertEqual(middleware.theme(self.request), {'THEME': 'auto'})

    def test_theme_user(self):
        user = create_user()
        user.user_settings.theme = 'DA'
        user.user_settings.save()
        self.request.user = user
        self.assertEqual(middleware.theme(self.request), {'THEME': 'dark'})

    def test_theme_without_user(self):
        self.assertEqual(middleware.theme(self.request), {'THEME': 'auto'})


class ErrorPagesMiddlewareTest(TestCase):
    '''
    Test the 405 page middleware
    '''

    def setUp(self):
        self.request = RequestFactory().get('/')
        self.request.user = AnonymousUser()

    @override_settings(DEBUG=False)
    def test_405_rendered(self):
        handler = middleware.ErrorPagesMiddleware(
                            lambda request: HttpResponseNotAllowed(['POST']))
        response = handler(self.request)
        self.assertEqual(response.status_code, 405)
        self.assertIn(b'405', response.content)
        self.assertEqual(response['Allow'], 'POST')

    @override_settings(DEBUG=False)
    def test_other_responses_untouched(self):
        original = HttpResponse('ok')
        handler = middleware.ErrorPagesMiddleware(lambda request: original)
        self.assertIs(handler(self.request), original)

    @override_settings(DEBUG=True)
    def test_debug_untouched(self):
        original = HttpResponseNotAllowed(['POST'])
        handler = middleware.ErrorPagesMiddleware(lambda request: original)
        self.assertIs(handler(self.request), original)
