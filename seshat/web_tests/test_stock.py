from selenium import webdriver
from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from django.urls import reverse
from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Permission

from stock import models

import os


class StockWebTests(StaticLiveServerTestCase):
    '''
    Test the views of stock application
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

        self.category = models.Category.objects.create(
                                name='New category')

        self.location = models.Location.objects.create(
                                name='New location')

        self.sublocation = models.SubLocation.objects.create(
                                location=self.location,
                                name='new sublocation')

        self.item = models.Item.objects.create(
                                code='code',
                                category=self.category,
                                location=self.sublocation,
                                price=50)

        self.assembled_item = models.Item.objects.create(
                                code='assembly code',
                                category=self.category,
                                location=self.sublocation,
                                price=50,
                                is_assembly=True)

        self.assembly_item = models.AssemblyItem.objects.create(
                                item=self.assembled_item,
                                sub_item=self.item,
                                quantity=5)

        self.item_move = models.ItemMove.objects.create(
                                item=self.item,
                                location=self.sublocation,
                                type=models.ItemMove.ADD,
                                related_to=models.ItemMove.PURCHASE,
                                quantity=20)

        self.assembled_item_move = models.ItemMove.objects.create(
                                item=self.assembled_item,
                                location=self.sublocation,
                                type=models.ItemMove.REMOVE,
                                related_to=models.ItemMove.SELL,
                                quantity=1)

        self.sub_item_move = models.ItemMove.objects.create(
                                item=self.assembly_item.sub_item,
                                location=self.sublocation,
                                type=models.ItemMove.REMOVE,
                                related_to=models.ItemMove.ASSEMBLY,
                                quantity=self.assembled_item_move.quantity *\
                                                self.assembly_item.quantity)

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

    def test_index(self):
        '''
        Test stock index page
        '''
        self.browser.get(self.live_server_url + reverse('account:login'))

        self.browser.find_element_by_name('username').send_keys(self.username)
        self.browser.find_element_by_name('password').send_keys(self.password)
        self.browser.find_element_by_id('login').click()

        self.browser.get(self.live_server_url + reverse('stock:index'))

    def test_categories_list(self):
        '''
        Test categories list page
        '''
        self.browser.get(self.live_server_url + reverse('account:login'))

        self.browser.find_element_by_name('username').send_keys(self.username)
        self.browser.find_element_by_name('password').send_keys(self.password)
        self.browser.find_element_by_id('login').click()

        self.browser.get(self.live_server_url + reverse(
                                                    'stock:categories_list'))

    def test_categories_list_new(self):
        '''
        Test categories list page with add category permission
        '''
        add_permission = Permission.objects.get(codename='add_category')
        self.user.user_permissions.add(add_permission)

        self.user.refresh_from_db()

        self.browser.get(self.live_server_url + reverse('account:login'))

        self.browser.find_element_by_name('username').send_keys(self.username)
        self.browser.find_element_by_name('password').send_keys(self.password)
        self.browser.find_element_by_id('login').click()

        self.browser.get(self.live_server_url + reverse(
                                                    'stock:categories_list'))

    def test_categories_list_change(self):
        '''
        Test categories list page with change category permission
        '''
        change_permission = Permission.objects.get(
                                            codename='change_category')
        self.user.user_permissions.add(change_permission)

        self.user.refresh_from_db()

        self.browser.get(self.live_server_url + reverse('account:login'))

        self.browser.find_element_by_name('username').send_keys(self.username)
        self.browser.find_element_by_name('password').send_keys(self.password)
        self.browser.find_element_by_id('login').click()

        self.browser.get(self.live_server_url + reverse(
                                                    'stock:categories_list'))

    def test_categories_list_delete(self):
        '''
        Test categories list page with delete category permission
        '''
        delete_permission = Permission.objects.get(codename='delete_category')
        self.user.user_permissions.add(delete_permission)

        self.user.refresh_from_db()

        self.browser.get(self.live_server_url + reverse('account:login'))

        self.browser.find_element_by_name('username').send_keys(self.username)
        self.browser.find_element_by_name('password').send_keys(self.password)
        self.browser.find_element_by_id('login').click()

        self.browser.get(self.live_server_url + reverse(
                                                    'stock:categories_list'))

    def test_new_category(self):
        '''
        Test new category page
        '''
        add_permission = Permission.objects.get(codename='add_category')
        self.user.user_permissions.add(add_permission)

        self.user.refresh_from_db()

        self.browser.get(self.live_server_url + reverse('account:login'))

        self.browser.find_element_by_name('username').send_keys(self.username)
        self.browser.find_element_by_name('password').send_keys(self.password)
        self.browser.find_element_by_id('login').click()

        self.browser.get(self.live_server_url + reverse(
                                                    'stock:category_new'))

    def test_edit_category(self):
        '''
        Test edit category page
        '''
        change_permission = Permission.objects.get(codename='change_category')
        self.user.user_permissions.add(change_permission)

        self.user.refresh_from_db()

        self.browser.get(self.live_server_url + reverse('account:login'))

        self.browser.find_element_by_name('username').send_keys(self.username)
        self.browser.find_element_by_name('password').send_keys(self.password)
        self.browser.find_element_by_id('login').click()

        self.browser.get(self.live_server_url + reverse(
                                            'stock:category_edit',
                                            kwargs={'pk': self.category.id}))

    def test_locations_list(self):
        '''
        Test locations list page
        '''
        self.browser.get(self.live_server_url + reverse('account:login'))

        self.browser.find_element_by_name('username').send_keys(self.username)
        self.browser.find_element_by_name('password').send_keys(self.password)
        self.browser.find_element_by_id('login').click()

        self.browser.get(self.live_server_url + reverse(
                                                    'stock:locations_list'))

    def test_locations_list_new(self):
        '''
        Test locations list page with add location permission
        '''
        add_permission = Permission.objects.get(codename='add_location')
        self.user.user_permissions.add(add_permission)

        self.user.refresh_from_db()

        self.browser.get(self.live_server_url + reverse('account:login'))

        self.browser.find_element_by_name('username').send_keys(self.username)
        self.browser.find_element_by_name('password').send_keys(self.password)
        self.browser.find_element_by_id('login').click()

        self.browser.get(self.live_server_url + reverse(
                                                    'stock:locations_list'))

    def test_locations_list_change(self):
        '''
        Test locations list page with change location permission
        '''
        change_permission = Permission.objects.get(
                                            codename='change_location')
        self.user.user_permissions.add(change_permission)

        self.user.refresh_from_db()

        self.browser.get(self.live_server_url + reverse('account:login'))

        self.browser.find_element_by_name('username').send_keys(self.username)
        self.browser.find_element_by_name('password').send_keys(self.password)
        self.browser.find_element_by_id('login').click()

        self.browser.get(self.live_server_url + reverse(
                                                    'stock:locations_list'))

    def test_locations_list_delete(self):
        '''
        Test locations list page with delete location permission
        '''
        delete_permission = Permission.objects.get(codename='delete_location')
        self.user.user_permissions.add(delete_permission)

        self.user.refresh_from_db()

        self.browser.get(self.live_server_url + reverse('account:login'))

        self.browser.find_element_by_name('username').send_keys(self.username)
        self.browser.find_element_by_name('password').send_keys(self.password)
        self.browser.find_element_by_id('login').click()

        self.browser.get(self.live_server_url + reverse(
                                                    'stock:locations_list'))

    def test_new_location(self):
        '''
        Test new location page
        '''
        add_permission = Permission.objects.get(codename='add_location')
        self.user.user_permissions.add(add_permission)

        self.user.refresh_from_db()

        self.browser.get(self.live_server_url + reverse('account:login'))

        self.browser.find_element_by_name('username').send_keys(self.username)
        self.browser.find_element_by_name('password').send_keys(self.password)
        self.browser.find_element_by_id('login').click()

        self.browser.get(self.live_server_url + reverse(
                                                    'stock:location_new'))

    def test_edit_location(self):
        '''
        Test edit location page
        '''
        change_permission = Permission.objects.get(codename='change_location')
        self.user.user_permissions.add(change_permission)

        self.user.refresh_from_db()

        self.browser.get(self.live_server_url + reverse('account:login'))

        self.browser.find_element_by_name('username').send_keys(self.username)
        self.browser.find_element_by_name('password').send_keys(self.password)
        self.browser.find_element_by_id('login').click()

        self.browser.get(self.live_server_url + reverse(
                                            'stock:location_edit',
                                            kwargs={'pk': self.location.id}))

    def test_sublocations_list(self):
        '''
        Test sublocations list page
        '''
        self.browser.get(self.live_server_url + reverse('account:login'))

        self.browser.find_element_by_name('username').send_keys(self.username)
        self.browser.find_element_by_name('password').send_keys(self.password)
        self.browser.find_element_by_id('login').click()

        self.browser.get(self.live_server_url + reverse(
                                                    'stock:sublocations_list'))

    def test_sublocations_list_new(self):
        '''
        Test sublocations list page with add sublocation permission
        '''
        add_permission = Permission.objects.get(codename='add_sublocation')
        self.user.user_permissions.add(add_permission)

        self.user.refresh_from_db()

        self.browser.get(self.live_server_url + reverse('account:login'))

        self.browser.find_element_by_name('username').send_keys(self.username)
        self.browser.find_element_by_name('password').send_keys(self.password)
        self.browser.find_element_by_id('login').click()

        self.browser.get(self.live_server_url + reverse(
                                                    'stock:sublocations_list'))

    def test_sublocations_list_change(self):
        '''
        Test sublocations list page with change sublocation permission
        '''
        change_permission = Permission.objects.get(
                                            codename='change_sublocation')
        self.user.user_permissions.add(change_permission)

        self.user.refresh_from_db()

        self.browser.get(self.live_server_url + reverse('account:login'))

        self.browser.find_element_by_name('username').send_keys(self.username)
        self.browser.find_element_by_name('password').send_keys(self.password)
        self.browser.find_element_by_id('login').click()

        self.browser.get(self.live_server_url + reverse(
                                                    'stock:sublocations_list'))

    def test_sublocations_list_delete(self):
        '''
        Test sublocations list page with delete sublocation permission
        '''
        delete_permission = Permission.objects.get(
                                                codename='delete_sublocation')
        self.user.user_permissions.add(delete_permission)

        self.user.refresh_from_db()

        self.browser.get(self.live_server_url + reverse('account:login'))

        self.browser.find_element_by_name('username').send_keys(self.username)
        self.browser.find_element_by_name('password').send_keys(self.password)
        self.browser.find_element_by_id('login').click()

        self.browser.get(self.live_server_url + reverse(
                                                    'stock:sublocations_list'))

    def test_new_sublocation(self):
        '''
        Test new sublocation page
        '''
        add_permission = Permission.objects.get(codename='add_sublocation')
        self.user.user_permissions.add(add_permission)

        self.user.refresh_from_db()

        self.browser.get(self.live_server_url + reverse('account:login'))

        self.browser.find_element_by_name('username').send_keys(self.username)
        self.browser.find_element_by_name('password').send_keys(self.password)
        self.browser.find_element_by_id('login').click()

        self.browser.get(self.live_server_url + reverse(
                                                    'stock:sublocation_new'))

    def test_edit_sublocation(self):
        '''
        Test edit sublocation page
        '''
        change_permission = Permission.objects.get(
                                                codename='change_sublocation')
        self.user.user_permissions.add(change_permission)

        self.user.refresh_from_db()

        self.browser.get(self.live_server_url + reverse('account:login'))

        self.browser.find_element_by_name('username').send_keys(self.username)
        self.browser.find_element_by_name('password').send_keys(self.password)
        self.browser.find_element_by_id('login').click()

        self.browser.get(self.live_server_url + reverse(
                                        'stock:sublocation_edit',
                                        kwargs={'pk': self.sublocation.id}))

    def test_items_list(self):
        '''
        Test items list page
        '''
        self.browser.get(self.live_server_url + reverse('account:login'))

        self.browser.find_element_by_name('username').send_keys(self.username)
        self.browser.find_element_by_name('password').send_keys(self.password)
        self.browser.find_element_by_id('login').click()

        self.browser.get(self.live_server_url + reverse(
                                                    'stock:items_list'))

    def test_items_list_new(self):
        '''
        Test items list page with add item permission
        '''
        add_permission = Permission.objects.get(codename='add_item')
        self.user.user_permissions.add(add_permission)

        self.user.refresh_from_db()

        self.browser.get(self.live_server_url + reverse('account:login'))

        self.browser.find_element_by_name('username').send_keys(self.username)
        self.browser.find_element_by_name('password').send_keys(self.password)
        self.browser.find_element_by_id('login').click()

        self.browser.get(self.live_server_url + reverse(
                                                    'stock:items_list'))

    def test_items_list_change(self):
        '''
        Test items list page with change item permission
        '''
        change_permission = Permission.objects.get(
                                            codename='change_item')
        self.user.user_permissions.add(change_permission)

        self.user.refresh_from_db()

        self.browser.get(self.live_server_url + reverse('account:login'))

        self.browser.find_element_by_name('username').send_keys(self.username)
        self.browser.find_element_by_name('password').send_keys(self.password)
        self.browser.find_element_by_id('login').click()

        self.browser.get(self.live_server_url + reverse(
                                                    'stock:items_list'))

    def test_items_list_delete(self):
        '''
        Test items list page with delete item permission
        '''
        delete_permission = Permission.objects.get(codename='delete_item')
        self.user.user_permissions.add(delete_permission)

        self.user.refresh_from_db()

        self.browser.get(self.live_server_url + reverse('account:login'))

        self.browser.find_element_by_name('username').send_keys(self.username)
        self.browser.find_element_by_name('password').send_keys(self.password)
        self.browser.find_element_by_id('login').click()

        self.browser.get(self.live_server_url + reverse(
                                                    'stock:items_list'))

    def test_new_item(self):
        '''
        Test new item page
        '''
        add_permission = Permission.objects.get(codename='add_item')
        self.user.user_permissions.add(add_permission)

        self.user.refresh_from_db()

        self.browser.get(self.live_server_url + reverse('account:login'))

        self.browser.find_element_by_name('username').send_keys(self.username)
        self.browser.find_element_by_name('password').send_keys(self.password)
        self.browser.find_element_by_id('login').click()

        self.browser.get(self.live_server_url + reverse(
                                                    'stock:item_new'))

    def test_edit_item(self):
        '''
        Test edit item page
        '''
        change_permission = Permission.objects.get(codename='change_item')
        self.user.user_permissions.add(change_permission)

        self.user.refresh_from_db()

        self.browser.get(self.live_server_url + reverse('account:login'))

        self.browser.find_element_by_name('username').send_keys(self.username)
        self.browser.find_element_by_name('password').send_keys(self.password)
        self.browser.find_element_by_id('login').click()

        self.browser.get(self.live_server_url + reverse(
                                            'stock:item_edit',
                                            kwargs={'pk': self.item.id}))

    def test_item_details(self):
        '''
        Test item details page
        '''
        self.browser.get(self.live_server_url + reverse('account:login'))

        self.browser.find_element_by_name('username').send_keys(self.username)
        self.browser.find_element_by_name('password').send_keys(self.password)
        self.browser.find_element_by_id('login').click()

        self.browser.get(self.live_server_url + reverse(
                                                'stock:item_details',
                                                kwargs={'pk': self.item.id}))

    def test_item_details_new(self):
        '''
        Test item details page with add item permission
        '''
        add_permission = Permission.objects.get(codename='add_item')
        self.user.user_permissions.add(add_permission)

        self.user.refresh_from_db()

        self.browser.get(self.live_server_url + reverse('account:login'))

        self.browser.find_element_by_name('username').send_keys(self.username)
        self.browser.find_element_by_name('password').send_keys(self.password)
        self.browser.find_element_by_id('login').click()

        self.browser.get(self.live_server_url + reverse(
                                                'stock:item_details',
                                                kwargs={'pk': self.item.id}))

    def test_item_details_change(self):
        '''
        Test item details page with change item permission
        '''
        change_permission = Permission.objects.get(
                                            codename='change_item')
        self.user.user_permissions.add(change_permission)

        self.user.refresh_from_db()

        self.browser.get(self.live_server_url + reverse('account:login'))

        self.browser.find_element_by_name('username').send_keys(self.username)
        self.browser.find_element_by_name('password').send_keys(self.password)
        self.browser.find_element_by_id('login').click()

        self.browser.get(self.live_server_url + reverse(
                                                'stock:item_details',
                                                kwargs={'pk': self.item.id}))

    def test_item_details_delete(self):
        '''
        Test item details page with delete item permission
        '''
        delete_permission = Permission.objects.get(codename='delete_item')
        self.user.user_permissions.add(delete_permission)

        self.user.refresh_from_db()

        self.browser.get(self.live_server_url + reverse('account:login'))

        self.browser.find_element_by_name('username').send_keys(self.username)
        self.browser.find_element_by_name('password').send_keys(self.password)
        self.browser.find_element_by_id('login').click()

        self.browser.get(self.live_server_url + reverse(
                                                'stock:item_details',
                                                kwargs={'pk': self.item.id}))

    def test_item_moves_list(self):
        '''
        Test items' moves list page
        '''
        self.browser.get(self.live_server_url + reverse('account:login'))

        self.browser.find_element_by_name('username').send_keys(self.username)
        self.browser.find_element_by_name('password').send_keys(self.password)
        self.browser.find_element_by_id('login').click()

        self.browser.get(self.live_server_url + reverse(
                                                'stock:moves_list',
                                                kwargs={'pk': self.item.id}))

    def test_new_item_move(self):
        '''
        Test new item's move page
        '''
        add_permission = Permission.objects.get(codename='add_itemmove')
        self.user.user_permissions.add(add_permission)

        self.user.refresh_from_db()

        self.browser.get(self.live_server_url + reverse('account:login'))

        self.browser.find_element_by_name('username').send_keys(self.username)
        self.browser.find_element_by_name('password').send_keys(self.password)
        self.browser.find_element_by_id('login').click()

        self.browser.get(self.live_server_url + reverse(
                                                'stock:move_new',
                                                kwargs={'pk': self.item.id}))

    def test_new_item_transfer(self):
        '''
        Test new item's transfer page
        '''
        add_permission = Permission.objects.get(codename='add_itemtransfer')
        self.user.user_permissions.add(add_permission)

        self.user.refresh_from_db()

        self.browser.get(self.live_server_url + reverse('account:login'))

        self.browser.find_element_by_name('username').send_keys(self.username)
        self.browser.find_element_by_name('password').send_keys(self.password)
        self.browser.find_element_by_id('login').click()

        self.browser.get(self.live_server_url + reverse(
                                                'stock:transfer_new',
                                                kwargs={'pk': self.item.id}))
