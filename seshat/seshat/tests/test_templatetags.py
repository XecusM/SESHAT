from django.template import Context, Template
from django.test import RequestFactory, SimpleTestCase

from seshat.templatetags import custom_tags


class CustomTagsTest(SimpleTestCase):
    '''
    Test the project template tags and filters
    '''

    def test_active_application(self):
        self.assertTrue(custom_tags.active_application('stock', '/stock/items/'))
        self.assertTrue(custom_tags.active_application('stock', '/ar/stock/'))
        self.assertFalse(custom_tags.active_application('stock', '/sales/'))
        self.assertFalse(custom_tags.active_application('stock', '/'))

    def test_query_string(self):
        request = RequestFactory().get('/', {'search': 'bolt', 'page': '2'})
        template = Template("{% load custom_tags %}{% query_string page=3 %}")
        result = template.render(Context({'request': request}))
        self.assertIn('search=bolt', result)
        self.assertIn('page=3', result)
        template = Template("{% load custom_tags %}{% query_string search='' page='' %}")
        self.assertEqual(template.render(Context({'request': request})), '?')

    def test_percentage(self):
        self.assertEqual(custom_tags.percentage(25, 100), 25)
        self.assertEqual(custom_tags.percentage(5, 0), 0)
        self.assertEqual(custom_tags.percentage(500, 100), 100)
        self.assertEqual(custom_tags.percentage('x', 100), 0)

    def test_call_method(self):
        self.assertEqual(custom_tags.call_method('abc', 'upper'), 'ABC')

    def test_initials(self):
        class Person:
            first_name = 'ada'
            last_name = 'lovelace'
        self.assertEqual(custom_tags.initials(Person()), 'AL')
        self.assertEqual(custom_tags.initials('zed'), 'Z')

    def test_to_query(self):
        self.assertEqual(custom_tags.to_query({'a': 1, 'b': 'x y'}), 'a=1&b=x+y')
        self.assertEqual(custom_tags.to_query(None), '')
