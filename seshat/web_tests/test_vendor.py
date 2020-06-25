from selenium import webdriver
from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from django.urls import reverse
from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Permission

from vendor import models

import os


class VendorWebTests(StaticLiveServerTestCase):
    '''
    Test the views of vendor application
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

        self.company = models.VendorCompany.objects.create(
                                                name='New Company')

        self.vendor = models.Vendor.objects.create(
                                                company=self.company,
                                                first_name='Mohamed',
                                                last_name='Aboel-fotouh')

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

    def test_companies_list(self):
        '''
        Test companies list page
        '''
        view_permission = Permission.objects.get(
                                            codename='view_vendorcompany')
        self.user.user_permissions.add(view_permission)

        self.user.refresh_from_db()

        self.browser.get(self.live_server_url + reverse('account:login'))

        self.browser.find_element_by_name('username').send_keys(self.username)
        self.browser.find_element_by_name('password').send_keys(self.password)
        self.browser.find_element_by_id('login').click()

        self.browser.get(self.live_server_url + reverse(
                                                    'vendor:companies_list'))

    def test_companies_list_new(self):
        '''
        Test companies list page with add company permission
        '''
        view_permission = Permission.objects.get(
                                            codename='view_vendorcompany')
        self.user.user_permissions.add(view_permission)

        add_permission = Permission.objects.get(
                                            codename='add_vendorcompany')
        self.user.user_permissions.add(add_permission)

        self.user.refresh_from_db()

        self.browser.get(self.live_server_url + reverse('account:login'))

        self.browser.find_element_by_name('username').send_keys(self.username)
        self.browser.find_element_by_name('password').send_keys(self.password)
        self.browser.find_element_by_id('login').click()

        self.browser.get(self.live_server_url + reverse(
                                                    'vendor:companies_list'))

    def test_companies_list_change(self):
        '''
        Test companies list page with change company permission
        '''
        view_permission = Permission.objects.get(
                                            codename='view_vendorcompany')
        self.user.user_permissions.add(view_permission)

        change_permission = Permission.objects.get(
                                            codename='change_vendorcompany')
        self.user.user_permissions.add(change_permission)

        self.user.refresh_from_db()

        self.browser.get(self.live_server_url + reverse('account:login'))

        self.browser.find_element_by_name('username').send_keys(self.username)
        self.browser.find_element_by_name('password').send_keys(self.password)
        self.browser.find_element_by_id('login').click()

        self.browser.get(self.live_server_url + reverse(
                                                    'vendor:companies_list'))

    def test_companies_list_delete(self):
        '''
        Test companies list page with delete company permission
        '''
        view_permission = Permission.objects.get(
                                            codename='view_vendorcompany')
        self.user.user_permissions.add(view_permission)

        delete_permission = Permission.objects.get(
                                            codename='delete_vendorcompany')
        self.user.user_permissions.add(delete_permission)

        self.user.refresh_from_db()

        self.browser.get(self.live_server_url + reverse('account:login'))

        self.browser.find_element_by_name('username').send_keys(self.username)
        self.browser.find_element_by_name('password').send_keys(self.password)
        self.browser.find_element_by_id('login').click()

        self.browser.get(self.live_server_url + reverse(
                                                    'vendor:companies_list'))

    def test_new_company(self):
        '''
        Test new company page
        '''
        view_permission = Permission.objects.get(
                                            codename='view_vendorcompany')
        self.user.user_permissions.add(view_permission)

        add_permission = Permission.objects.get(
                                            codename='add_vendorcompany')
        self.user.user_permissions.add(add_permission)

        self.user.refresh_from_db()

        self.browser.get(self.live_server_url + reverse('account:login'))

        self.browser.find_element_by_name('username').send_keys(self.username)
        self.browser.find_element_by_name('password').send_keys(self.password)
        self.browser.find_element_by_id('login').click()

        self.browser.get(self.live_server_url + reverse(
                                                    'vendor:company_new'))

    def test_edit_company(self):
        '''
        Test edit company page
        '''
        view_permission = Permission.objects.get(
                                            codename='view_vendorcompany')
        self.user.user_permissions.add(view_permission)

        change_permission = Permission.objects.get(
                                            codename='change_vendorcompany')
        self.user.user_permissions.add(change_permission)

        self.user.refresh_from_db()

        self.browser.get(self.live_server_url + reverse('account:login'))

        self.browser.find_element_by_name('username').send_keys(self.username)
        self.browser.find_element_by_name('password').send_keys(self.password)
        self.browser.find_element_by_id('login').click()

        self.browser.get(self.live_server_url + reverse(
                                            'vendor:company_edit',
                                            kwargs={'pk': self.company.id}))

    def test_company_details(self):
        '''
        Test edit company page
        '''
        view_permission = Permission.objects.get(
                                            codename='view_vendorcompany')
        self.user.user_permissions.add(view_permission)

        self.user.refresh_from_db()

        self.browser.get(self.live_server_url + reverse('account:login'))

        self.browser.find_element_by_name('username').send_keys(self.username)
        self.browser.find_element_by_name('password').send_keys(self.password)
        self.browser.find_element_by_id('login').click()

        self.browser.get(self.live_server_url + reverse(
                                            'vendor:company_details',
                                            kwargs={'pk': self.company.id}))

    def test_company_details_change(self):
        '''
        Test edit company page with change company permission
        '''
        view_permission = Permission.objects.get(
                                            codename='view_vendorcompany')
        self.user.user_permissions.add(view_permission)

        change_permission = Permission.objects.get(
                                            codename='change_vendorcompany')
        self.user.user_permissions.add(change_permission)

        self.user.refresh_from_db()

        self.browser.get(self.live_server_url + reverse('account:login'))

        self.browser.find_element_by_name('username').send_keys(self.username)
        self.browser.find_element_by_name('password').send_keys(self.password)
        self.browser.find_element_by_id('login').click()

        self.browser.get(self.live_server_url + reverse(
                                            'vendor:company_details',
                                            kwargs={'pk': self.company.id}))

    def test_company_details_delete(self):
        '''
        Test edit company page with delete company permission
        '''
        view_permission = Permission.objects.get(
                                            codename='view_vendorcompany')
        self.user.user_permissions.add(view_permission)

        delete_permission = Permission.objects.get(
                                            codename='delete_vendorcompany')
        self.user.user_permissions.add(delete_permission)

        self.user.refresh_from_db()

        self.browser.get(self.live_server_url + reverse('account:login'))

        self.browser.find_element_by_name('username').send_keys(self.username)
        self.browser.find_element_by_name('password').send_keys(self.password)
        self.browser.find_element_by_id('login').click()

        self.browser.get(self.live_server_url + reverse(
                                            'vendor:company_details',
                                            kwargs={'pk': self.company.id}))

    def test_vendors_list(self):
        '''
        Test vendors list page
        '''
        company_permission = Permission.objects.get(
                                            codename='view_vendorcompany')
        self.user.user_permissions.add(company_permission)

        view_permission = Permission.objects.get(
                                            codename='view_vendor')
        self.user.user_permissions.add(view_permission)

        self.user.refresh_from_db()

        self.browser.get(self.live_server_url + reverse('account:login'))

        self.browser.find_element_by_name('username').send_keys(self.username)
        self.browser.find_element_by_name('password').send_keys(self.password)
        self.browser.find_element_by_id('login').click()

        self.browser.get(self.live_server_url + reverse(
                                                    'vendor:vendors_list'))

    def test_vendors_list_new(self):
        '''
        Test vendors list page with add vendor permission
        '''
        company_permission = Permission.objects.get(
                                            codename='view_vendorcompany')
        self.user.user_permissions.add(company_permission)

        view_permission = Permission.objects.get(
                                            codename='view_vendor')
        self.user.user_permissions.add(view_permission)

        add_permission = Permission.objects.get(
                                            codename='add_vendor')
        self.user.user_permissions.add(add_permission)

        self.user.refresh_from_db()

        self.browser.get(self.live_server_url + reverse('account:login'))

        self.browser.find_element_by_name('username').send_keys(self.username)
        self.browser.find_element_by_name('password').send_keys(self.password)
        self.browser.find_element_by_id('login').click()

        self.browser.get(self.live_server_url + reverse(
                                                    'vendor:vendors_list'))

    def test_vendors_list_change(self):
        '''
        Test vendors list page with change vendor permission
        '''
        company_permission = Permission.objects.get(
                                            codename='view_vendorcompany')
        self.user.user_permissions.add(company_permission)

        view_permission = Permission.objects.get(
                                            codename='view_vendor')
        self.user.user_permissions.add(view_permission)

        change_permission = Permission.objects.get(
                                            codename='change_vendor')
        self.user.user_permissions.add(change_permission)

        self.user.refresh_from_db()

        self.browser.get(self.live_server_url + reverse('account:login'))

        self.browser.find_element_by_name('username').send_keys(self.username)
        self.browser.find_element_by_name('password').send_keys(self.password)
        self.browser.find_element_by_id('login').click()

        self.browser.get(self.live_server_url + reverse(
                                                    'vendor:vendors_list'))

    def test_vendors_list_delete(self):
        '''
        Test vendors list page with delete vendor permission
        '''
        company_permission = Permission.objects.get(
                                            codename='view_vendorcompany')
        self.user.user_permissions.add(company_permission)

        view_permission = Permission.objects.get(
                                            codename='view_vendor')
        self.user.user_permissions.add(view_permission)

        delete_permission = Permission.objects.get(
                                            codename='delete_vendor')
        self.user.user_permissions.add(delete_permission)

        self.user.refresh_from_db()

        self.browser.get(self.live_server_url + reverse('account:login'))

        self.browser.find_element_by_name('username').send_keys(self.username)
        self.browser.find_element_by_name('password').send_keys(self.password)
        self.browser.find_element_by_id('login').click()

        self.browser.get(self.live_server_url + reverse(
                                                    'vendor:vendors_list'))

    def test_new_vendor(self):
        '''
        Test new vendor page
        '''
        company_permission = Permission.objects.get(
                                            codename='view_vendorcompany')
        self.user.user_permissions.add(company_permission)

        view_permission = Permission.objects.get(
                                            codename='view_vendor')
        self.user.user_permissions.add(view_permission)

        add_permission = Permission.objects.get(
                                            codename='add_vendor')
        self.user.user_permissions.add(add_permission)

        self.user.refresh_from_db()

        self.browser.get(self.live_server_url + reverse('account:login'))

        self.browser.find_element_by_name('username').send_keys(self.username)
        self.browser.find_element_by_name('password').send_keys(self.password)
        self.browser.find_element_by_id('login').click()

        self.browser.get(self.live_server_url + reverse(
                                            'vendor:vendor_new',
                                            kwargs={'pk': self.company.id}))

    def test_edit_vendor(self):
        '''
        Test edit vendor page
        '''
        company_permission = Permission.objects.get(
                                            codename='view_vendorcompany')
        self.user.user_permissions.add(company_permission)

        view_permission = Permission.objects.get(
                                            codename='view_vendor')
        self.user.user_permissions.add(view_permission)

        change_permission = Permission.objects.get(
                                            codename='change_vendor')
        self.user.user_permissions.add(change_permission)

        self.user.refresh_from_db()

        self.browser.get(self.live_server_url + reverse('account:login'))

        self.browser.find_element_by_name('username').send_keys(self.username)
        self.browser.find_element_by_name('password').send_keys(self.password)
        self.browser.find_element_by_id('login').click()

        self.browser.get(self.live_server_url + reverse(
                                            'vendor:vendor_edit',
                                            kwargs={'pk': self.vendor.id}))

    def test_vendor_details(self):
        '''
        Test edit vendor page
        '''
        company_permission = Permission.objects.get(
                                            codename='view_vendorcompany')
        self.user.user_permissions.add(company_permission)

        view_permission = Permission.objects.get(
                                            codename='view_vendor')
        self.user.user_permissions.add(view_permission)

        self.user.refresh_from_db()

        self.browser.get(self.live_server_url + reverse('account:login'))

        self.browser.find_element_by_name('username').send_keys(self.username)
        self.browser.find_element_by_name('password').send_keys(self.password)
        self.browser.find_element_by_id('login').click()

        self.browser.get(self.live_server_url + reverse(
                                            'vendor:vendor_details',
                                            kwargs={'pk': self.vendor.id}))

    def test_vendor_details_change(self):
        '''
        Test edit vendor page with change vendor permission
        '''
        company_permission = Permission.objects.get(
                                            codename='view_vendorcompany')
        self.user.user_permissions.add(company_permission)

        view_permission = Permission.objects.get(
                                            codename='view_vendor')
        self.user.user_permissions.add(view_permission)

        change_permission = Permission.objects.get(
                                            codename='change_vendor')
        self.user.user_permissions.add(change_permission)

        self.user.refresh_from_db()

        self.browser.get(self.live_server_url + reverse('account:login'))

        self.browser.find_element_by_name('username').send_keys(self.username)
        self.browser.find_element_by_name('password').send_keys(self.password)
        self.browser.find_element_by_id('login').click()

        self.browser.get(self.live_server_url + reverse(
                                            'vendor:vendor_details',
                                            kwargs={'pk': self.vendor.id}))

    def test_vendor_details_delete(self):
        '''
        Test edit vendor page with delete vendor permission
        '''
        company_permission = Permission.objects.get(
                                            codename='view_vendorcompany')
        self.user.user_permissions.add(company_permission)

        view_permission = Permission.objects.get(
                                            codename='view_vendor')
        self.user.user_permissions.add(view_permission)

        delete_permission = Permission.objects.get(
                                            codename='delete_vendor')
        self.user.user_permissions.add(delete_permission)

        self.user.refresh_from_db()

        self.browser.get(self.live_server_url + reverse('account:login'))

        self.browser.find_element_by_name('username').send_keys(self.username)
        self.browser.find_element_by_name('password').send_keys(self.password)
        self.browser.find_element_by_id('login').click()

        self.browser.get(self.live_server_url + reverse(
                                            'vendor:vendor_details',
                                            kwargs={'pk': self.vendor.id}))
