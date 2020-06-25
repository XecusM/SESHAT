from selenium import webdriver
from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from django.urls import reverse
from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Permission

from purchase import models
from vendor import models as vendors_models
from stock import models as stock_models

import os


class PuchaseWebTests(StaticLiveServerTestCase):
    '''
    Test the views of purchase application
    '''
    reset_sequences = True
    serialized_rollback = True

    def setUp(self):
        '''
        Initiate every test
        '''
        self.username = 'username'
        self.password = 'testpassword'

        self.user = get_user_model().objects.create_user(
                                    first_name='Mohamed',
                                    last_name='Aboel-fotouh',
                                    username=self.username,
                                    password=self.password,)

        self.company = vendors_models.VendorCompany.objects.create(
                                                name='New Company')

        self.category = stock_models.Category.objects.create(
                                                name='new category')
        self.location = stock_models.Location.objects.create(
                                                name='new location')
        self.sub_location = stock_models.SubLocation.objects.create(
                                                location=self.location,
                                                name='new sub_location')
        self.item = stock_models.Item.objects.create(
                                                code='code',
                                                category=self.category,
                                                location=self.sub_location,
                                                price=50)
        self.move = stock_models.ItemMove.objects.create(
                                    item=self.item,
                                    type=stock_models.ItemMove.ADD,
                                    related_to=stock_models.ItemMove.PURCHASE,
                                    location=self.sub_location,
                                    quantity=5)

        self.order = models.PurchaseOrder.objects.create(company=self.company)

        self.purchase_item = models.PurchaseItems.objects.create(
                                    order=self.order,
                                    item=self.move,
                                    price=50)

        if os.name == 'nt':
            self.browser = webdriver.Firefox(
                            executable_path=os.path.join(
                                    settings.BASE_DIR,
                                    'web_tests/geckodriver.exe'))
        else:
            self.browser = webdriver.Firefox(
                            executable_path=os.path.join(
                                    settings.BASE_DIR,
                                    'web_tests/geckodriver'))

        self.addCleanup(self.browser.quit)

    def tearDown(self):
        '''
        Initial method after all tests
        '''
        links = [
                link.get_attribute('href')
                for link in self.browser.find_elements_by_tag_name('a')
        ]

        for link in links:
            if 'logout' in link or '#' in link:
                pass
            else:
                self.browser.get(link)

                page_source = self.browser.page_source

                if 'error number 400' in page_source:
                    error_number = '400'
                elif 'error number 403' in page_source:
                    error_number = '403'
                elif 'error number 404' in page_source:
                    error_number = '404'
                elif 'error number 500' in page_source:
                    error_number = '500'
                else:
                    error_number = 'Passed'

                self.assertEqual('Passed', error_number)

        self.browser.get(self.live_server_url + reverse('account:logout'))

    def test_orders_list(self):
        '''
        Test orders list page
        '''
        view_permission = Permission.objects.get(
                                            codename='view_purchaseorder')
        self.user.user_permissions.add(view_permission)

        self.user.refresh_from_db()

        self.browser.get(self.live_server_url + reverse('account:login'))

        self.browser.find_element_by_name('username').send_keys(self.username)
        self.browser.find_element_by_name('password').send_keys(self.password)
        self.browser.find_element_by_id('login').click()

        self.browser.get(self.live_server_url + reverse(
                                                    'purchase:orders_list'))

    def test_orders_list_new(self):
        '''
        Test orders list page with add permission
        '''
        view_permission = Permission.objects.get(
                                            codename='view_purchaseorder')
        self.user.user_permissions.add(view_permission)

        add_permission = Permission.objects.get(
                                            codename='add_purchaseorder')
        self.user.user_permissions.add(add_permission)

        self.user.refresh_from_db()

        self.browser.get(self.live_server_url + reverse('account:login'))

        self.browser.find_element_by_name('username').send_keys(self.username)
        self.browser.find_element_by_name('password').send_keys(self.password)
        self.browser.find_element_by_id('login').click()

        self.browser.get(self.live_server_url + reverse(
                                                    'purchase:orders_list'))

    def test_orders_list_change(self):
        '''
        Test orders list page with change permission
        '''
        view_permission = Permission.objects.get(
                                            codename='view_purchaseorder')
        self.user.user_permissions.add(view_permission)

        change_permission = Permission.objects.get(
                                            codename='change_purchaseorder')
        self.user.user_permissions.add(change_permission)

        self.user.refresh_from_db()

        self.browser.get(self.live_server_url + reverse('account:login'))

        self.browser.find_element_by_name('username').send_keys(self.username)
        self.browser.find_element_by_name('password').send_keys(self.password)
        self.browser.find_element_by_id('login').click()

        self.browser.get(self.live_server_url + reverse(
                                                    'purchase:orders_list'))

    def test_orders_list_delete(self):
        '''
        Test orders list page with delete permission
        '''
        view_permission = Permission.objects.get(
                                            codename='view_purchaseorder')
        self.user.user_permissions.add(view_permission)

        delete_permission = Permission.objects.get(
                                            codename='delete_purchaseorder')
        self.user.user_permissions.add(delete_permission)

        self.user.refresh_from_db()

        self.browser.get(self.live_server_url + reverse('account:login'))

        self.browser.find_element_by_name('username').send_keys(self.username)
        self.browser.find_element_by_name('password').send_keys(self.password)
        self.browser.find_element_by_id('login').click()

        self.browser.get(self.live_server_url + reverse(
                                                    'purchase:orders_list'))

    def test_new_order(self):
        '''
        Test new order page
        '''
        view_permission = Permission.objects.get(
                                            codename='view_purchaseorder')
        self.user.user_permissions.add(view_permission)

        add_permission = Permission.objects.get(
                                            codename='add_purchaseorder')
        self.user.user_permissions.add(add_permission)

        self.user.refresh_from_db()

        self.browser.get(self.live_server_url + reverse('account:login'))

        self.browser.find_element_by_name('username').send_keys(self.username)
        self.browser.find_element_by_name('password').send_keys(self.password)
        self.browser.find_element_by_id('login').click()

        self.browser.get(self.live_server_url + reverse(
                                                    'purchase:order_new'))

    def test_edit_order(self):
        '''
        Test edit order page
        '''
        view_permission = Permission.objects.get(
                                            codename='view_purchaseorder')
        self.user.user_permissions.add(view_permission)

        change_permission = Permission.objects.get(
                                            codename='change_purchaseorder')
        self.user.user_permissions.add(change_permission)

        self.user.refresh_from_db()

        self.browser.get(self.live_server_url + reverse('account:login'))

        self.browser.find_element_by_name('username').send_keys(self.username)
        self.browser.find_element_by_name('password').send_keys(self.password)
        self.browser.find_element_by_id('login').click()

        self.browser.get(self.live_server_url + reverse(
                                            'purchase:order_edit',
                                            kwargs={'pk': self.order.id}))

    def test_order_details(self):
        '''
        Test edit order page
        '''
        view_permission = Permission.objects.get(
                                            codename='view_purchaseorder')
        self.user.user_permissions.add(view_permission)

        self.user.refresh_from_db()

        self.browser.get(self.live_server_url + reverse('account:login'))

        self.browser.find_element_by_name('username').send_keys(self.username)
        self.browser.find_element_by_name('password').send_keys(self.password)
        self.browser.find_element_by_id('login').click()

        self.browser.get(self.live_server_url + reverse(
                                            'purchase:order_details',
                                            kwargs={'pk': self.order.id}))

    def test_order_details_change(self):
        '''
        Test edit order page with change order permission
        '''
        view_permission = Permission.objects.get(
                                            codename='view_purchaseorder')
        self.user.user_permissions.add(view_permission)

        change_permission = Permission.objects.get(
                                            codename='change_purchaseorder')
        self.user.user_permissions.add(change_permission)

        self.user.refresh_from_db()

        self.browser.get(self.live_server_url + reverse('account:login'))

        self.browser.find_element_by_name('username').send_keys(self.username)
        self.browser.find_element_by_name('password').send_keys(self.password)
        self.browser.find_element_by_id('login').click()

        self.browser.get(self.live_server_url + reverse(
                                            'purchase:order_details',
                                            kwargs={'pk': self.order.id}))

    def test_order_details_delete(self):
        '''
        Test edit order page with delete order permission
        '''
        view_permission = Permission.objects.get(
                                            codename='view_purchaseorder')
        self.user.user_permissions.add(view_permission)

        delete_permission = Permission.objects.get(
                                            codename='delete_purchaseorder')
        self.user.user_permissions.add(delete_permission)

        self.user.refresh_from_db()

        self.browser.get(self.live_server_url + reverse('account:login'))

        self.browser.find_element_by_name('username').send_keys(self.username)
        self.browser.find_element_by_name('password').send_keys(self.password)
        self.browser.find_element_by_id('login').click()

        self.browser.get(self.live_server_url + reverse(
                                            'purchase:order_details',
                                            kwargs={'pk': self.order.id}))
