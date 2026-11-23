from django.test import RequestFactory, TestCase
from django.urls import reverse

from seshat import functools
from seshat.testing import create_user, create_stock
from stock.models import Category


class NextUrlTest(TestCase):
    '''
    Test the safe next url helper
    '''

    def test_local_next(self):
        request = RequestFactory().get('/', {'next': '/stock/'})
        self.assertEqual(functools.get_next_url(request, '/'), '/stock/')

    def test_post_next(self):
        request = RequestFactory().post('/', {'next': '/sales/'})
        self.assertEqual(functools.get_next_url(request, '/'), '/sales/')

    def test_external_next_rejected(self):
        request = RequestFactory().get('/', {'next': 'https://evil.example.com/'})
        self.assertEqual(functools.get_next_url(request, '/home/'), '/home/')

    def test_missing_next(self):
        self.assertEqual(functools.get_next_url(RequestFactory().get('/'), '/x/'), '/x/')


class PaginateMixinTest(TestCase):
    '''
    Test the page limit from the user's settings
    '''

    def test_paginate_by(self):
        mixin = functools.PaginateMixin()
        mixin.request = RequestFactory().get('/')
        mixin.request.user = create_user()
        mixin.request.user.user_settings.paginate = 12
        self.assertEqual(mixin.get_paginate_by(None), 12)

    def test_paginate_default(self):
        mixin = functools.PaginateMixin()
        mixin.request = RequestFactory().get('/')
        mixin.request.user = object()
        self.assertEqual(mixin.get_paginate_by(None), 30)


class DeleteObjectTest(TestCase):
    '''
    Test the shared delete helper
    '''

    def setUp(self):
        self.request = RequestFactory().post('/')
        self.request.user = create_user()
        from django.contrib.messages.storage.fallback import FallbackStorage
        self.request.session = {}
        self.request._messages = FallbackStorage(self.request)

    def test_delete(self):
        category = Category.objects.create(name='Gone')
        response = functools.delete_object(
                        self.request, Category, category.pk,
                        lambda obj: f'Category-{obj.name}', '/list/')
        self.assertEqual(response.url, '/list/')
        self.assertFalse(Category.objects.filter(pk=category.pk).exists())

    def test_linked_object_not_deleted(self):
        item = create_stock()
        response = functools.delete_object(
                        self.request, Category, item.category.pk,
                        lambda obj: f'Category-{obj.name}', '/list/', '/details/')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'/details/', response.content)
        self.assertTrue(Category.objects.filter(pk=item.category.pk).exists())

    def test_missing_object(self):
        from django.http import Http404
        with self.assertRaises(Http404):
            functools.delete_object(self.request, Category, 999, str, reverse('Index'))
