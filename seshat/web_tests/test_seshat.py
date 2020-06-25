from selenium import webdriver
from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from django.urls import reverse
from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Permission

import os


class SeshatWebTests(StaticLiveServerTestCase):
    '''
    Test the views of seshat application
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
            if 'logout' in link or 'download' in link or '#' in link:
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
        Test index page
        '''
        self.browser.get(self.live_server_url + reverse('account:login'))

        self.browser.find_element_by_name('username').send_keys(self.username)
        self.browser.find_element_by_name('password').send_keys(self.password)
        self.browser.find_element_by_id('login').click()

        self.browser.get(self.live_server_url + reverse('index'))

    def test_backup(self):
        '''
        Test backup page
        '''
        view_permission = Permission.objects.get(codename='backup')
        self.user.user_permissions.add(view_permission)

        self.user.refresh_from_db()

        self.browser.get(self.live_server_url + reverse('account:login'))

        self.browser.find_element_by_name('username').send_keys(self.username)
        self.browser.find_element_by_name('password').send_keys(self.password)
        self.browser.find_element_by_id('login').click()

        self.browser.get(self.live_server_url + reverse('backup'))

    def test_restore(self):
        '''
        Test restore page
        '''
        view_permission = Permission.objects.get(codename='restore')
        self.user.user_permissions.add(view_permission)

        self.user.refresh_from_db()

        self.browser.get(self.live_server_url + reverse('account:login'))

        self.browser.find_element_by_name('username').send_keys(self.username)
        self.browser.find_element_by_name('password').send_keys(self.password)
        self.browser.find_element_by_id('login').click()

        self.browser.get(self.live_server_url + reverse('restore'))

    def test_export(self):
        '''
        Test export page
        '''
        view_permission = Permission.objects.get(codename='export')
        self.user.user_permissions.add(view_permission)

        self.user.refresh_from_db()

        self.browser.get(self.live_server_url + reverse('account:login'))

        self.browser.find_element_by_name('username').send_keys(self.username)
        self.browser.find_element_by_name('password').send_keys(self.password)
        self.browser.find_element_by_id('login').click()

        self.browser.get(self.live_server_url + reverse('export'))

    def test_import(self):
        '''
        Test import page
        '''
        view_permission = Permission.objects.get(codename='import')
        self.user.user_permissions.add(view_permission)

        self.user.refresh_from_db()

        self.browser.get(self.live_server_url + reverse('account:login'))

        self.browser.find_element_by_name('username').send_keys(self.username)
        self.browser.find_element_by_name('password').send_keys(self.password)
        self.browser.find_element_by_id('login').click()

        self.browser.get(self.live_server_url + reverse('import'))
