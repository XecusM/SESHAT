import logging

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from django_db_logger.models import StatusLog
from x_django_app.models import XActivity

from account import models
from account.functools import get_user_permission_names
from seshat.testing import (
                        TempDirsTestCase, PASSWORD, create_user,
                        create_superuser, image_file, )


class LoginLogoutTest(TestCase):
    '''
    Test logging in and out
    '''

    def setUp(self):
        self.user = create_user('john')

    def test_login_page(self):
        response = self.client.get(reverse('account:Login'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'account/login.html')

    def test_login_redirects_to_default_page(self):
        self.user.user_settings.default_page = models.Settings.STOCK
        self.user.user_settings.save()
        response = self.client.post(
                        reverse('account:Login'),
                        {'username': 'JOHN', 'password': PASSWORD})
        self.assertRedirects(response, reverse('stock:Index'), fetch_redirect_response=False)

    def test_login_uses_user_language(self):
        self.user.user_settings.language = 'ar'
        self.user.user_settings.save()
        response = self.client.post(
                        reverse('account:Login'),
                        {'username': 'john', 'password': PASSWORD})
        self.assertEqual(response.url, '/ar/')
        self.assertEqual(response.cookies['django_language'].value, 'ar')

    def test_login_next_url(self):
        response = self.client.post(
                        reverse('account:Login') + '?next=/stock/items/',
                        {'username': 'john', 'password': PASSWORD,
                         'next': '/stock/items/'})
        self.assertEqual(response.url, '/stock/items/')

    def test_login_rejects_external_next(self):
        response = self.client.post(
                        reverse('account:Login'),
                        {'username': 'john', 'password': PASSWORD,
                         'next': 'https://evil.example.com/'})
        self.assertEqual(response.url, reverse('Index'))

    def test_logged_in_user_redirected_from_login(self):
        self.client.force_login(self.user)
        response = self.client.get(reverse('account:Login'))
        self.assertEqual(response.status_code, 302)

    def test_logout_requires_post(self):
        self.client.force_login(self.user)
        self.assertEqual(self.client.get(reverse('account:Logout')).status_code, 405)
        response = self.client.post(reverse('account:Logout'))
        self.assertEqual(response.status_code, 302)
        self.assertNotIn('_auth_user_id', self.client.session)


class IndexViewTest(TestCase):
    '''
    Test the administration dashboard
    '''

    def test_requires_admin_permission(self):
        self.client.force_login(create_user())
        self.assertEqual(self.client.get(reverse('account:Index')).status_code, 403)

    def test_anonymous_redirected(self):
        response = self.client.get(reverse('account:Index'))
        self.assertRedirects(
                response, '/admin/login/?next=/admin/', fetch_redirect_response=False)

    def test_dashboard_context(self):
        StatusLog.objects.create(logger_name='x', level=logging.ERROR, msg='boom')
        self.client.force_login(create_superuser())
        response = self.client.get(reverse('account:Index'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['errors_count'], 1)
        self.assertEqual(response.context['users_count'], 1)

    def test_partial_permission(self):
        self.client.force_login(create_user(permissions=['account.backup']))
        response = self.client.get(reverse('account:Index'))
        self.assertEqual(response.status_code, 200)
        self.assertNotIn('users_count', response.context)


class UserViewsTest(TestCase):
    '''
    Test creating, listing, viewing and editing accounts
    '''

    def setUp(self):
        self.admin = create_superuser()
        self.client.force_login(self.admin)

    def test_new_user(self):
        response = self.client.post(reverse('account:NewUser'), {
                    'first_name': 'Ann', 'last_name': 'Lee', 'username': 'ann',
                    'password1': PASSWORD, 'password2': PASSWORD,
                    'is_active': 'on', 'permissions': ['stock.add_item']})
        user = get_user_model().objects.get(username='ann')
        self.assertRedirects(response, reverse('account:UserDetails', kwargs={'pk': user.pk}))
        self.assertIn('stock.view_item', get_user_permission_names(user))
        self.assertTrue(XActivity.objects.filter(
                        activity=XActivity.CREATE, message='Account-ann').exists())

    def test_new_user_invalid(self):
        response = self.client.post(reverse('account:NewUser'), {'username': ''})
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.context['form'].errors)

    def test_users_list_and_search(self):
        create_user('zed')
        response = self.client.get(reverse('account:UsersList'), {'search': 'zed'})
        self.assertEqual([u.username for u in response.context['users_list']], ['zed'])

    def test_users_list_permission(self):
        self.client.force_login(create_user('nobody'))
        self.assertEqual(self.client.get(reverse('account:UsersList')).status_code, 403)

    def test_user_details_own_and_other(self):
        user = create_user('own')
        self.client.force_login(user)
        self.assertEqual(self.client.get(
                reverse('account:UserDetails', kwargs={'pk': user.pk})).status_code, 200)
        self.assertEqual(self.client.get(
                reverse('account:UserDetails', kwargs={'pk': self.admin.pk})).status_code, 403)

    def test_user_details_missing(self):
        self.assertEqual(self.client.get(
                reverse('account:UserDetails', kwargs={'pk': 999})).status_code, 404)

    def test_edit_user(self):
        user = create_user('old')
        response = self.client.post(
                    reverse('account:EditUser', kwargs={'pk': user.pk}),
                    {'first_name': 'New', 'last_name': 'Name', 'username': 'new',
                     'is_active': 'on'})
        self.assertRedirects(response, reverse('account:UserDetails', kwargs={'pk': user.pk}))
        user.refresh_from_db()
        self.assertEqual((user.username, user.first_name), ('new', 'New'))

    def test_non_admin_cannot_edit_admin(self):
        self.client.force_login(create_user(permissions=['account.change_user']))
        response = self.client.get(reverse('account:EditUser', kwargs={'pk': self.admin.pk}))
        self.assertEqual(response.status_code, 403)

    def test_edit_permissions(self):
        user = create_user('perm')
        response = self.client.post(
                    reverse('account:EditPermission', kwargs={'pk': user.pk}),
                    {'permissions': ['vendor.add_vendor']})
        self.assertRedirects(response, reverse('account:DetailedPermission', kwargs={'pk': user.pk}))
        names = get_user_permission_names(user)
        self.assertIn('vendor.view_vendor', names)
        self.assertIn('vendor.view_vendorcompany', names)

    def test_permission_pages(self):
        user = create_user('perm')
        for name in ['account:EditPermission', 'account:DetailedPermission']:
            response = self.client.get(reverse(name, kwargs={'pk': user.pk}))
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.context['account'], user)


class DeleteUserViewTest(TestCase):
    '''
    Test deleting accounts
    '''

    def setUp(self):
        self.admin = create_superuser()
        self.client.force_login(self.admin)

    def test_delete_user(self):
        user = create_user('gone')
        response = self.client.post(reverse('account:DeleteUser', kwargs={'pk': user.pk}))
        self.assertRedirects(response, reverse('account:UsersList'))
        self.assertFalse(get_user_model().objects.filter(pk=user.pk).exists())

    def test_delete_requires_post(self):
        user = create_user('stay')
        response = self.client.get(reverse('account:DeleteUser', kwargs={'pk': user.pk}))
        self.assertEqual(response.status_code, 405)

    def test_cannot_delete_self(self):
        response = self.client.post(reverse('account:DeleteUser', kwargs={'pk': self.admin.pk}))
        self.assertTemplateUsed(response, 'error_message.html')
        self.assertTrue(get_user_model().objects.filter(pk=self.admin.pk).exists())

    def test_delete_requires_permission(self):
        user = create_user('stay')
        self.client.force_login(create_user('weak'))
        response = self.client.post(reverse('account:DeleteUser', kwargs={'pk': user.pk}))
        self.assertEqual(response.status_code, 403)


class OwnAccountViewsTest(TempDirsTestCase):
    '''
    Test the pages a user manages for themselves
    '''

    def setUp(self):
        self.user = create_user('self')
        self.client.force_login(self.user)

    def test_edit_profile(self):
        url = reverse('account:EditProfile', kwargs={'pk': self.user.user_profile.pk})
        response = self.client.post(url, {'email': 'self@example.com', 'phone': ''})
        self.assertRedirects(response, reverse('account:UserDetails', kwargs={'pk': self.user.pk}))
        self.user.user_profile.refresh_from_db()
        self.assertEqual(self.user.user_profile.email, 'self@example.com')

    def test_cannot_edit_other_profile(self):
        other = create_user('other')
        url = reverse('account:EditProfile', kwargs={'pk': other.user_profile.pk})
        self.assertEqual(self.client.get(url).status_code, 403)

    def test_edit_settings_switches_language(self):
        url = reverse('account:EditSettings', kwargs={'pk': self.user.user_settings.pk})
        response = self.client.post(url, {
                    'language': 'ar', 'theme': 'DA', 'paginate': 10, 'default_page': 'IN'})
        self.assertEqual(response.url, f'/ar/admin/details/{self.user.pk}/')
        self.user.user_settings.refresh_from_db()
        self.assertEqual(self.user.user_settings.theme, 'DA')

    def test_cannot_edit_other_settings(self):
        other = create_user('other')
        url = reverse('account:EditSettings', kwargs={'pk': other.user_settings.pk})
        self.assertEqual(self.client.get(url).status_code, 403)

    def test_photo_edit_and_remove(self):
        url = reverse('account:PhotoEdit', kwargs={'pk': self.user.user_photo.pk})
        response = self.client.post(url, {'photo': image_file()})
        self.assertEqual(response.status_code, 302)
        self.user.user_photo.refresh_from_db()
        self.assertTrue(self.user.user_photo.photo)

        response = self.client.post(reverse('account:PhotoRemove', kwargs={'pk': self.user.pk}))
        self.assertEqual(response.status_code, 302)
        self.user.user_photo.refresh_from_db()
        self.assertFalse(self.user.user_photo.photo)

    def test_cannot_remove_other_photo(self):
        other = create_user('other')
        response = self.client.post(reverse('account:PhotoRemove', kwargs={'pk': other.pk}))
        self.assertEqual(response.status_code, 403)

    def test_toggle_theme(self):
        url = reverse('account:ToggleTheme')
        self.client.post(url, {'current': 'light', 'next': '/stock/'})
        self.user.user_settings.refresh_from_db()
        self.assertEqual(self.user.user_settings.theme, models.Settings.DARK)
        response = self.client.post(url, {'next': '/stock/'})
        self.assertEqual(response.url, '/stock/')
        self.user.user_settings.refresh_from_db()
        self.assertEqual(self.user.user_settings.theme, models.Settings.LIGHT)

    def test_toggle_theme_auto_dark(self):
        self.client.post(reverse('account:ToggleTheme'), {'current': 'dark'})
        self.user.user_settings.refresh_from_db()
        self.assertEqual(self.user.user_settings.theme, models.Settings.LIGHT)

    def test_theme_in_template(self):
        self.user.user_settings.theme = models.Settings.DARK
        self.user.user_settings.save()
        response = self.client.get(reverse('Index'))
        self.assertContains(response, 'data-bs-theme="dark"')


class PasswordViewsTest(TestCase):
    '''
    Test changing and resetting passwords
    '''

    def test_change_password_flow(self):
        user = create_user('pw')
        self.client.force_login(user)
        response = self.client.post(
                    reverse('account:PasswordChange', kwargs={'pk': user.pk}),
                    {'old_password': PASSWORD,
                     'new_password1': 'Brand-New-Password-9',
                     'new_password2': 'Brand-New-Password-9'})
        self.assertRedirects(response, reverse('account:PasswordChangeDone'))
        user.refresh_from_db()
        self.assertTrue(user.check_password('Brand-New-Password-9'))
        # the done page can be opened once
        self.assertEqual(self.client.get(reverse('account:PasswordChangeDone')).status_code, 403)

    def test_cannot_change_other_password(self):
        self.client.force_login(create_user('a'))
        other = create_user('b')
        url = reverse('account:PasswordChange', kwargs={'pk': other.pk})
        self.assertEqual(self.client.get(url).status_code, 403)

    def test_reset_password(self):
        user = create_user('reset')
        self.client.force_login(create_user('boss', permissions=['account.reset_password']))
        response = self.client.post(
                    reverse('account:PasswordReset', kwargs={'pk': user.pk}),
                    {'new_password1': 'Reset-Password-77', 'new_password2': 'Reset-Password-77'})
        self.assertRedirects(response, reverse('account:UserDetails', kwargs={'pk': user.pk}),
                             fetch_redirect_response=False)
        user.refresh_from_db()
        self.assertTrue(user.check_password('Reset-Password-77'))
        self.assertTrue(XActivity.objects.filter(activity=XActivity.RESET).exists())

    def test_reset_password_mismatch(self):
        user = create_user('reset')
        self.client.force_login(create_superuser())
        response = self.client.post(
                    reverse('account:PasswordReset', kwargs={'pk': user.pk}),
                    {'new_password1': 'Reset-Password-77', 'new_password2': 'Other-Password-88'})
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.context['form'].errors)

    def test_reset_admin_password_forbidden(self):
        admin = create_superuser()
        self.client.force_login(create_user('boss', permissions=['account.reset_password']))
        response = self.client.get(reverse('account:PasswordReset', kwargs={'pk': admin.pk}))
        self.assertEqual(response.status_code, 403)


class ActivityViewsTest(TestCase):
    '''
    Test activities, logs and reports
    '''

    def setUp(self):
        self.admin = create_superuser()
        self.user = create_user('worker')
        XActivity.objects.create_activity(
                activity_object=self.user, activity=XActivity.EDIT,
                user=self.user, message='worker edit')
        XActivity.objects.create_activity(
                activity_object=self.admin, activity=XActivity.CREATE,
                user=self.admin, message='admin create')

    def test_user_activities_own(self):
        self.client.force_login(self.user)
        response = self.client.get(reverse('account:UserActivities', kwargs={'pk': self.user.pk}))
        self.assertEqual([a.message for a in response.context['object_list']], ['worker edit'])
        response = self.client.get(reverse('account:UserActivities', kwargs={'pk': self.admin.pk}))
        self.assertEqual(response.status_code, 403)

    def test_activities_list_filters(self):
        self.client.force_login(self.admin)
        url = reverse('account:ActivitiesList')
        self.assertEqual(len(self.client.get(url).context['object_list']), 2)
        response = self.client.get(url, {'activity': XActivity.CREATE})
        self.assertEqual([a.message for a in response.context['object_list']], ['admin create'])
        response = self.client.get(url, {'from_date': '2000-01-01', 'to_date': '2000-01-02'})
        self.assertEqual(len(response.context['object_list']), 0)

    def test_logs(self):
        log = StatusLog.objects.create(logger_name='db', level=logging.ERROR, msg='broken')
        self.client.force_login(self.admin)
        self.assertContains(self.client.get(reverse('account:LogEntryList')), 'broken')
        self.assertContains(
                self.client.get(reverse('account:DetailedLogEntry', kwargs={'pk': log.pk})), 'broken')

    def test_logs_permission(self):
        self.client.force_login(self.user)
        self.assertEqual(self.client.get(reverse('account:LogEntryList')).status_code, 403)

    def test_reports(self):
        self.client.force_login(self.user)
        self.assertEqual(self.client.get(
                reverse('account:UserReport', kwargs={'pk': self.user.pk})).status_code, 200)
        self.assertEqual(self.client.get(
                reverse('account:UserReport', kwargs={'pk': self.admin.pk})).status_code, 403)
        self.assertEqual(self.client.get(reverse('account:ActivitiesReport')).status_code, 403)

        data = self.client.get(reverse('account:APIReportUser', kwargs={'pk': self.user.pk})).json()
        self.assertEqual(sum(data['total']), 1)
        self.assertEqual(self.client.get(
                reverse('account:APIReportUser', kwargs={'pk': self.admin.pk})).status_code, 403)
        self.assertEqual(self.client.get(reverse('account:APIReportActivities')).status_code, 403)

    def test_activities_report_api(self):
        self.client.force_login(self.admin)
        self.assertEqual(self.client.get(reverse('account:ActivitiesReport')).status_code, 200)
        data = self.client.get(reverse('account:APIReportActivities')).json()
        self.assertEqual(sum(data['total']), 2)

    def test_report_api_anonymous(self):
        response = self.client.get(reverse('account:APIReportActivities'))
        self.assertIn(response.status_code, (401, 403))
