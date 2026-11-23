from django.test import TestCase
from django.urls import reverse

from account import functools, models
from seshat.testing import create_user


class PermissionsListTest(TestCase):
    '''
    Every permission on the permissions page must exist
    '''

    def test_all_permissions_exist(self):
        for name in functools.all_permission_names():
            self.assertIsNotNone(functools.get_permission(name), name)

    def test_implied_permissions_exist(self):
        for sources, target in functools.implied_permissions:
            self.assertIsNotNone(functools.get_permission(target), target)
            for name in sources:
                self.assertIsNotNone(functools.get_permission(name), name)

    def test_unknown_permission(self):
        self.assertIsNone(functools.get_permission('account.unknown'))


class SetPermissionsTest(TestCase):
    '''
    Test giving permissions to a user
    '''

    def test_set_permissions_adds_implied_view(self):
        user = create_user()
        functools.set_permissions(user, ['customer.add_customer'])
        names = functools.get_user_permission_names(user)
        self.assertIn('customer.add_customer', names)
        self.assertIn('customer.view_customer', names)
        self.assertIn('customer.view_customercompany', names)

    def test_set_permissions_removes_unselected(self):
        user = create_user(permissions=['stock.add_item'])
        functools.set_permissions(user, [])
        self.assertNotIn('stock.add_item', functools.get_user_permission_names(user))

    def test_chained_implications(self):
        user = create_user()
        functools.set_permissions(user, ['sale.add_saleorder'])
        names = functools.get_user_permission_names(user)
        for name in ['sale.view_saleorder', 'stock.view_item',
                     'customer.view_customercompany']:
            self.assertIn(name, names)

    def test_check_permissions_without_permissions(self):
        user = create_user()
        functools.check_permissions(user)
        self.assertEqual(functools.get_user_permission_names(user), set())


class UrlLinkTest(TestCase):
    '''
    Test the default page url
    '''

    def test_default_pages(self):
        user = create_user()
        expected = {
            models.Settings.INDEX: reverse('Index'),
            models.Settings.ADMIN: reverse('account:Index'),
            models.Settings.STOCK: reverse('stock:Index'),
            models.Settings.CUSTOMER: reverse('customer:CompaniesList'),
            models.Settings.VENDOR: reverse('vendor:CompaniesList'),
            models.Settings.PURCHASE: reverse('purchase:OrdersList'),
            models.Settings.SALE: reverse('sale:OrdersList'),
        }
        for page, url in expected.items():
            user.user_settings.default_page = page
            self.assertEqual(functools.get_url_link(user), url)
