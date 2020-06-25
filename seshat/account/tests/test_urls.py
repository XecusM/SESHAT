# event test_urls.py
from django.test import TestCase
from django.urls import reverse, resolve

from django.contrib.auth import views as auth_views
from account import views


class AccountUrlsTest(TestCase):
    '''
    Test all urls in the account applciation
    '''
    def test_account_index_resolved(self):
        '''
        Test account index url
        '''
        url = reverse('account:index')
        self.assertEquals(
                        resolve(url).func.view_class,
                        views.Index)

    def test_login_resolved(self):
        '''
        Test login url
        '''
        url = reverse('account:login')
        self.assertEquals(
                        resolve(url).func.view_class,
                        views.Login)

    def test_logout_resolved(self):
        '''
        Test logout url
        '''
        url = reverse('account:logout')
        self.assertEquals(
                        resolve(url).func.view_class,
                        auth_views.LogoutView)

    def test_new_resolved(self):
        '''
        Test new user account url
        '''
        url = reverse('account:new')
        self.assertEquals(
                        resolve(url).func.view_class,
                        views.New)

    def test_edit_resolved(self):
        '''
        Test edit user account url
        '''
        url = reverse('account:edit', kwargs={'pk': 1})
        self.assertEquals(
                        resolve(url).func.view_class,
                        views.Edit)

    def test_details_resolved(self):
        '''
        Test user account details url
        '''
        url = reverse('account:details', kwargs={'pk': 1})
        self.assertEquals(
                        resolve(url).func.view_class,
                        views.Details)

    def test_list_resolved(self):
        '''
        Test list user accounts url
        '''
        url = reverse('account:list')
        self.assertEquals(
                        resolve(url).func.view_class,
                        views.List)

    def test_delete_resolved(self):
        '''
        Test delete user account url
        '''
        url = reverse('account:delete', kwargs={'pk': 1})
        self.assertEquals(
                        resolve(url).func,
                        views.delete)

    def test_profile_details_resolved(self):
        '''
        Test user profile details url
        '''
        url = reverse('account:profile_details', kwargs={'pk': 1})
        self.assertEquals(
                        resolve(url).func.view_class,
                        views.ProfileDetails)

    def test_edit_profile_resolved(self):
        '''
        Test edit user profile url
        '''
        url = reverse('account:profile_edit', kwargs={'pk': 1})
        self.assertEquals(
                        resolve(url).func.view_class,
                        views.EditProfile)

    def test_settings_details_resolved(self):
        '''
        Test user settings details url
        '''
        url = reverse('account:settings_details', kwargs={'pk': 1})
        self.assertEquals(
                        resolve(url).func.view_class,
                        views.SettingsDetails)

    def test_edit_settings_resolved(self):
        '''
        Test edit user settings url
        '''
        url = reverse('account:settings_edit', kwargs={'pk': 1})
        self.assertEquals(
                        resolve(url).func.view_class,
                        views.EditSettings)

    def test_activities_list_resolved(self):
        '''
        Test list of activities of user account url
        '''
        url = reverse('account:activities_list', kwargs={'pk': 1})
        self.assertEquals(
                        resolve(url).func.view_class,
                        views.ActivitiesList)

    def test_password_change_resolved(self):
        '''
        Test change password url
        '''
        url = reverse('account:password_change', kwargs={'pk': 1})
        self.assertEquals(
                        resolve(url).func.view_class,
                        views.PasswordChange)

    def test_password_change_done_resolved(self):
        '''
        Test change password done url
        '''
        url = reverse('account:password_change_done')
        self.assertEquals(
                        resolve(url).func.view_class,
                        views.PasswordChangeDone)

    def test_reset_password_resolved(self):
        '''
        Test reset password url
        '''
        url = reverse('account:reset_password', kwargs={'pk': 1})
        self.assertEquals(
                        resolve(url).func,
                        views.reset_password)
