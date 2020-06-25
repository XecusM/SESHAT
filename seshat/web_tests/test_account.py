from selenium import webdriver
from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from django.urls import reverse
from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Permission

import os


class AccountWebTests(StaticLiveServerTestCase):
    '''
    Test the views of account application
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

        self.another_user = get_user_model().objects.create_user(
                                    first_name='Mohamed',
                                    last_name='Aboel-fotouh',
                                    username='other',
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
        Test account index page
        '''
        view_permission = Permission.objects.get(codename='view_user')
        self.user.user_permissions.add(view_permission)

        self.user.refresh_from_db()

        self.browser.get(self.live_server_url + reverse('account:login'))

        self.browser.find_element_by_name('username').send_keys(self.username)
        self.browser.find_element_by_name('password').send_keys(self.password)
        self.browser.find_element_by_id('login').click()

        self.browser.get(self.live_server_url + reverse('account:index'))

    def test_users_list(self):
        '''
        Test users list page
        '''
        view_permission = Permission.objects.get(codename='view_user')
        self.user.user_permissions.add(view_permission)

        self.user.refresh_from_db()

        self.browser.get(self.live_server_url + reverse('account:login'))

        self.browser.find_element_by_name('username').send_keys(self.username)
        self.browser.find_element_by_name('password').send_keys(self.password)
        self.browser.find_element_by_id('login').click()

        self.browser.get(self.live_server_url + reverse('account:list'))

    def test_users_list_change(self):
        '''
        Test users list page with change user permission
        '''
        view_permission = Permission.objects.get(codename='view_user')
        self.user.user_permissions.add(view_permission)

        change_permission = Permission.objects.get(codename='change_user')
        self.user.user_permissions.add(change_permission)

        self.user.refresh_from_db()

        self.browser.get(self.live_server_url + reverse('account:login'))

        self.browser.find_element_by_name('username').send_keys(self.username)
        self.browser.find_element_by_name('password').send_keys(self.password)
        self.browser.find_element_by_id('login').click()

        self.browser.get(self.live_server_url + reverse('account:list'))

    def test_users_list_delete(self):
        '''
        Test users list page with delete user permission
        '''
        view_permission = Permission.objects.get(codename='view_user')
        self.user.user_permissions.add(view_permission)

        delete_permission = Permission.objects.get(codename='delete_user')
        self.user.user_permissions.add(delete_permission)

        self.user.refresh_from_db()

        self.browser.get(self.live_server_url + reverse('account:login'))

        self.browser.find_element_by_name('username').send_keys(self.username)
        self.browser.find_element_by_name('password').send_keys(self.password)
        self.browser.find_element_by_id('login').click()

        self.browser.get(self.live_server_url + reverse('account:list'))

    def test_new_user(self):
        '''
        Test create new user page
        '''
        view_permission = Permission.objects.get(codename='view_user')
        self.user.user_permissions.add(view_permission)

        add_permission = Permission.objects.get(codename='add_user')
        self.user.user_permissions.add(add_permission)

        self.user.refresh_from_db()

        self.browser.get(self.live_server_url + reverse('account:login'))

        self.browser.find_element_by_name('username').send_keys(self.username)
        self.browser.find_element_by_name('password').send_keys(self.password)
        self.browser.find_element_by_id('login').click()

        self.browser.get(self.live_server_url + reverse('account:new'))

    def test_edit_user(self):
        '''
        Test edit user page
        '''
        view_permission = Permission.objects.get(codename='view_user')
        self.user.user_permissions.add(view_permission)

        add_permission = Permission.objects.get(codename='change_user')
        self.user.user_permissions.add(add_permission)

        self.user.refresh_from_db()

        self.browser.get(self.live_server_url + reverse('account:login'))

        self.browser.find_element_by_name('username').send_keys(self.username)
        self.browser.find_element_by_name('password').send_keys(self.password)
        self.browser.find_element_by_id('login').click()

        self.browser.get(self.live_server_url + reverse(
                                        'account:edit',
                                        kwargs={'pk': self.another_user.id}))

    def test_user_details(self):
        '''
        Test user details page
        '''
        view_permission = Permission.objects.get(codename='view_user')
        self.user.user_permissions.add(view_permission)

        self.user.refresh_from_db()

        self.browser.get(self.live_server_url + reverse('account:login'))

        self.browser.find_element_by_name('username').send_keys(self.username)
        self.browser.find_element_by_name('password').send_keys(self.password)
        self.browser.find_element_by_id('login').click()

        self.browser.get(self.live_server_url + reverse(
                                        'account:details',
                                        kwargs={'pk': self.another_user.id}))

    def test_user_profile(self):
        '''
        Test user profile page
        '''
        view_permission = Permission.objects.get(codename='view_user')
        self.user.user_permissions.add(view_permission)

        self.user.refresh_from_db()

        self.browser.get(self.live_server_url + reverse('account:login'))

        self.browser.find_element_by_name('username').send_keys(self.username)
        self.browser.find_element_by_name('password').send_keys(self.password)
        self.browser.find_element_by_id('login').click()

        self.browser.get(self.live_server_url + reverse(
                                'account:profile_details',
                                kwargs={
                                        'pk':
                                        self.another_user.user_profile.id}))

    def test_edit_user_profile(self):
        '''
        Test edit user profile page
        '''
        self.browser.get(self.live_server_url + reverse('account:login'))

        self.browser.find_element_by_name('username').send_keys(self.username)
        self.browser.find_element_by_name('password').send_keys(self.password)
        self.browser.find_element_by_id('login').click()

        self.browser.get(self.live_server_url + reverse(
                                    'account:profile_edit',
                                    kwargs={'pk': self.user.user_profile.id}))

    def test_user_settings(self):
        '''
        Test user settings page
        '''
        self.browser.get(self.live_server_url + reverse('account:login'))

        self.browser.find_element_by_name('username').send_keys(self.username)
        self.browser.find_element_by_name('password').send_keys(self.password)
        self.browser.find_element_by_id('login').click()

        self.browser.get(self.live_server_url + reverse(
                                'account:settings_details',
                                kwargs={'pk': self.user.user_settings.id}))

    def test_edit_user_settings(self):
        '''
        Test edit user settings page
        '''
        self.browser.get(self.live_server_url + reverse('account:login'))

        self.browser.find_element_by_name('username').send_keys(self.username)
        self.browser.find_element_by_name('password').send_keys(self.password)
        self.browser.find_element_by_id('login').click()

        self.browser.get(self.live_server_url + reverse(
                                'account:settings_edit',
                                kwargs={'pk': self.user.user_settings.id}))

    def test_user_activity(self):
        '''
        Test user activity page
        '''
        view_permission = Permission.objects.get(codename='view_user')
        self.user.user_permissions.add(view_permission)

        activity_permission = Permission.objects.get(codename='view_activity')
        self.user.user_permissions.add(activity_permission)

        self.user.refresh_from_db()

        self.browser.get(self.live_server_url + reverse('account:login'))

        self.browser.find_element_by_name('username').send_keys(self.username)
        self.browser.find_element_by_name('password').send_keys(self.password)
        self.browser.find_element_by_id('login').click()

        self.browser.get(self.live_server_url + reverse(
                                        'account:activities_list',
                                        kwargs={'pk': self.another_user.id}))

    def test_all_activities(self):
        '''
        Test all activities page
        '''
        view_permission = Permission.objects.get(codename='view_activity')
        self.user.user_permissions.add(view_permission)

        self.user.refresh_from_db()

        self.browser.get(self.live_server_url + reverse('account:login'))

        self.browser.find_element_by_name('username').send_keys(self.username)
        self.browser.find_element_by_name('password').send_keys(self.password)
        self.browser.find_element_by_id('login').click()

        self.browser.get(self.live_server_url + reverse(
                                            'account:all_activities_list'))

    def test_user_reset_password(self):
        '''
        Test user reset password page
        '''
        view_permission = Permission.objects.get(codename='view_user')
        self.user.user_permissions.add(view_permission)

        password_permission = Permission.objects.get(codename='reset_password')
        self.user.user_permissions.add(password_permission)

        self.user.refresh_from_db()

        self.browser.get(self.live_server_url + reverse('account:login'))

        self.browser.find_element_by_name('username').send_keys(self.username)
        self.browser.find_element_by_name('password').send_keys(self.password)
        self.browser.find_element_by_id('login').click()

        self.browser.get(self.live_server_url + reverse(
                                        'account:reset_password',
                                        kwargs={'pk': self.another_user.id}))

    def test_user_change_password(self):
        '''
        Test user change password page
        '''
        self.browser.get(self.live_server_url + reverse('account:login'))

        self.browser.find_element_by_name('username').send_keys(self.username)
        self.browser.find_element_by_name('password').send_keys(self.password)
        self.browser.find_element_by_id('login').click()

        self.browser.get(self.live_server_url + reverse(
                                            'account:password_change',
                                            kwargs={'pk': self.user.id}))
