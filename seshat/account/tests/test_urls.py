from django.contrib.auth import views as auth_views
from django.test import SimpleTestCase
from django.urls import reverse, resolve

from account import views


class AccountUrlsTest(SimpleTestCase):
    '''
    Every account url resolves to its view
    '''

    def assertResolves(self, name, view, kwargs=None):
        match = resolve(reverse(name, kwargs=kwargs))
        target = getattr(match.func, 'view_class', match.func)
        self.assertEqual(target, view, name)

    def test_urls(self):
        cases = [
            ('account:Index', views.Index, None),
            ('account:Login', views.Login, None),
            ('account:Logout', auth_views.LogoutView, None),
            ('account:ToggleTheme', views.toggle_theme, None),
            ('account:NewUser', views.NewUser, None),
            ('account:UsersList', views.UsersList, None),
            ('account:UserDetails', views.UserDetails, {'pk': 1}),
            ('account:EditUser', views.EditUser, {'pk': 1}),
            ('account:EditPermission', views.EditPermission, {'pk': 1}),
            ('account:DetailedPermission', views.DetailedPermission, {'pk': 1}),
            ('account:EditSettings', views.EditSettings, {'pk': 1}),
            ('account:EditProfile', views.EditProfile, {'pk': 1}),
            ('account:PhotoEdit', views.PhotoEdit, {'pk': 1}),
            ('account:PhotoRemove', views.photo_remove, {'pk': 1}),
            ('account:UserActivities', views.UserActivities, {'pk': 1}),
            ('account:UserReport', views.UserReport, {'pk': 1}),
            ('account:ActivitiesList', views.ActivitiesList, None),
            ('account:ActivitiesReport', views.ActivitiesReport, None),
            ('account:PasswordChange', views.PasswordChange, {'pk': 1}),
            ('account:PasswordChangeDone', views.PasswordChangeDone, None),
            ('account:DeleteUser', views.delete_user, {'pk': 1}),
            ('account:PasswordReset', views.reset_password, {'pk': 1}),
            ('account:LogEntryList', views.LogEntryList, None),
            ('account:DetailedLogEntry', views.DetailedLogEntry, {'pk': 1}),
        ]
        for name, view, kwargs in cases:
            self.assertResolves(name, view, kwargs)

    def test_api_urls(self):
        self.assertEqual(
                    resolve(reverse('account:APIReportUser', kwargs={'pk': 1})).func.cls.__name__,
                    'report_user_activity')
        self.assertEqual(
                    resolve(reverse('account:APIReportActivities')).func.cls.__name__,
                    'report_all_activities')

    def test_arabic_prefix(self):
        from django.utils import translation
        with translation.override('ar'):
            self.assertEqual(reverse('account:Login'), '/ar/admin/login/')
