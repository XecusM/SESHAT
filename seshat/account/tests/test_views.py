from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Permission


class AccountViewsTests(TestCase):
    '''
    Test all views for account application
    '''
    def setUp(self):
        '''
        Test intiation
        '''
        self.first_name = 'Mohamed'
        self.last_name = 'Aboel-fotouh'
        self.username = 'username'
        self.password = 'Testpass123'

        self.user = get_user_model().objects.create_user(
                                    first_name=self.first_name,
                                    last_name=self.last_name,
                                    username=self.username,
                                    password=self.password,
        )

        self.login_url = reverse('account:login')
        self.index_url = reverse('account:index')
        self.new_url = reverse('account:new')
        self.list_url = reverse('account:list')
        self.details_url = reverse(
                                    'account:details',
                                    kwargs={'pk': self.user.id}
        )
        self.edit_url = reverse(
                                    'account:edit',
                                    kwargs={'pk': self.user.id}
        )
        self.profile_details_url = reverse(
                                    'account:profile_details',
                                    kwargs={'pk': self.user.user_profile.id}
        )
        self.profile_edit_url = reverse(
                                    'account:profile_edit',
                                    kwargs={'pk': self.user.user_profile.id}
        )
        self.password_change_url = reverse(
                                    'account:password_change',
                                    kwargs={'pk': self.user.id}
        )
        self.reset_password_url = reverse(
                                    'account:reset_password',
                                    kwargs={'pk': self.user.id}
        )
        self.delete_url = reverse(
                                    'account:delete',
                                    kwargs={'pk': self.user.id}
        )
        self.activities_url = reverse(
                                    'account:activities_list',
                                    kwargs={'pk': self.user.id}
        )
        self.all_activities_url = reverse('account:all_activities_list')
        self.settings_details_url = reverse(
                                    'account:settings_details',
                                    kwargs={'pk': self.user.user_settings.id}
        )
        self.settings_edit_url = reverse(
                                    'account:settings_edit',
                                    kwargs={'pk': self.user.user_settings.id}
        )

    def test_login_get(self):
        '''
        Test get to login page
        '''
        response = self.client.get(self.login_url)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'account/login.html')

    def test_login_post(self):
        '''
        Test post to login page
        '''
        payload = {
                    'username': self.username,
                    'password': self.password,
        }

        response = self.client.post(self.login_url, data=payload)

        self.assertTrue(self.user.is_authenticated)

    def test_index_get(self):
        '''
        Test get to account index page
        '''
        permission = Permission.objects.get(codename='view_user')
        self.user.user_permissions.add(permission)

        self.user.refresh_from_db()

        response = self.client.get(self.index_url)

        self.assertEqual(response.status_code, 302)

        self.client.force_login(self.user)

        response = self.client.get(self.index_url)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'account/index.html')

    def test_new_user_get(self):
        '''
        Test get url for creating new user
        '''
        permission = Permission.objects.get(codename='add_user')
        self.user.user_permissions.add(permission)

        self.user.refresh_from_db()

        self.client.force_login(self.user)

        response = self.client.get(self.new_url)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'account/new.html')

    def test_new_user_permission(self):
        '''
        Test permissions for creating new user
        '''
        self.client.force_login(self.user)

        response = self.client.get(self.new_url)

        self.assertEqual(response.status_code, 403)

    def test_new_user_post(self):
        '''
        Test post url for creating new user
        '''
        permission = Permission.objects.get(codename='add_user')
        self.user.user_permissions.add(permission)

        self.user.refresh_from_db()

        self.client.force_login(self.user)

        response = self.client.post(self.new_url,
                                    data={
                                        'first_name': 'Mohamed',
                                        'last_name': 'Aboel-fotouh',
                                        'username': 'username2',
                                        'password1': self.password,
                                        'password2': self.password
                                    })

        self.assertEqual(response.status_code, 302)
        self.assertEquals(get_user_model().objects.all().count(), 2)

    def test_list_user_get(self):
        '''
        Test get url for list of all users
        '''
        permission = Permission.objects.get(codename='view_user')
        self.user.user_permissions.add(permission)

        self.user.refresh_from_db()

        self.client.force_login(self.user)

        response = self.client.get(self.list_url)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'account/list.html')

    def test_details_user_get(self):
        '''
        Test get url for user details
        '''
        self.client.force_login(self.user)

        response = self.client.get(self.details_url)

        self.assertEqual(response.status_code, 200)

    def test_edit_user_get(self):
        '''
        Test get url for edit user details
        '''
        permission = Permission.objects.get(codename='change_user')
        self.user.user_permissions.add(permission)

        self.user.refresh_from_db()

        self.client.force_login(self.user)

        response = self.client.get(self.edit_url)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'account/edit.html')

    def test_edit_user_permission(self):
        '''
        Test permissions url for edit details
        '''
        self.client.force_login(self.user)

        response = self.client.get(self.edit_url)

        self.assertEqual(response.status_code, 403)

    def test_edit_user_post(self):
        '''
        Test post url for edit details
        '''
        permission = Permission.objects.get(codename='change_user')
        self.user.user_permissions.add(permission)

        self.user.refresh_from_db()

        self.client.force_login(self.user)

        payload = {
                    'first_name': 'Another name',
                    'last_name': self.last_name,
                    'username': self.username,
                }

        response = self.client.post(self.edit_url, data=payload)

        self.assertEqual(response.status_code, 302)

        self.user.refresh_from_db()

        self.assertEqual(self.user.first_name, payload['first_name'])

    def test_details_user_profile_get(self):
        '''
        Test get url for user profile
        '''
        self.client.force_login(self.user)

        response = self.client.get(self.profile_details_url)

        self.assertEqual(response.status_code, 200)

    def test_edit_user_profile_get(self):
        '''
        Test get url for edit user profile
        '''
        self.client.force_login(self.user)

        response = self.client.get(self.profile_edit_url)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'account/profile_edit.html')

    def test_edit_user_profile_permission(self):
        '''
        Test permissions url for edit profile
        '''
        user = get_user_model().objects.create_user(
                                    first_name=self.first_name,
                                    last_name=self.last_name,
                                    username='username2',
                                    password=self.password,
        )

        self.client.force_login(user)

        response = self.client.get(self.profile_edit_url)

        self.assertEqual(response.status_code, 403)

    def test_edit_user_profile_post(self):
        '''
        Test post url for edit profile
        '''
        self.client.force_login(self.user)

        payload = {'email': 'user@email.com', }

        response = self.client.post(self.profile_edit_url, data=payload)

        self.assertEqual(response.status_code, 302)

        self.user.refresh_from_db()

        self.assertEqual(self.user.user_profile.email, payload['email'])

    def test_password_change_get(self):
        '''
        Test get url for change password
        '''
        self.client.force_login(self.user)

        response = self.client.get(self.password_change_url)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'account/password_change.html')

    def test_password_change_permission(self):
        '''
        Test permissions url for edit profile
        '''
        user = get_user_model().objects.create_user(
                                    first_name=self.first_name,
                                    last_name=self.last_name,
                                    username='username2',
                                    password=self.password,
        )

        self.client.force_login(user)

        response = self.client.get(self.password_change_url)

        self.assertEqual(response.status_code, 403)

    def test_password_change_post(self):
        '''
        Test post url for edit profile
        '''
        self.client.force_login(self.user)

        payload = {'email': 'user@email.com', }

        response = self.client.post(self.password_change_url, data=payload)

        self.assertEqual(response.status_code, 302)

        self.user.refresh_from_db()

        self.assertEqual(self.user.user_profile.email, payload['email'])

    def test_password_change_get(self):
        '''
        Test get to edit change password
        '''
        self.client.force_login(self.user)

        response = self.client.get(self.password_change_url)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response,
                                'account/password_change.html')

    def test_password_change_permission(self):
        '''
        Test get user to change another user password
        '''
        user = get_user_model().objects.create_user(
                                    first_name=self.first_name,
                                    last_name=self.last_name,
                                    username='username2',
                                    password=self.password,
        )

        self.client.force_login(user)

        response = self.client.get(self.password_change_url)

        self.assertEqual(response.status_code, 403)

    def test_password_change_post(self):
        '''
        Test pass user change password
        '''
        self.client.force_login(self.user)

        payload = {
            'old_password': self.password,
            'new_password1': 'newtestpassword',
            'new_password2': 'newtestpassword',
        }

        self.client.post(
                        self.password_change_url,
                        data=payload,
                        follow=True
        )

        self.user.refresh_from_db()

        self.assertTrue(self.user.check_password(payload['new_password1']))

    def test_user_delete_get(self):
        '''
        Test get url for delete user
        '''
        permission = Permission.objects.get(codename='delete_user')
        self.user.user_permissions.add(permission)

        self.user.refresh_from_db()

        self.client.force_login(self.user)

        response = self.client.get(self.delete_url)

        self.assertEqual(response.status_code, 404)

    def test_user_delete_permission(self):
        '''
        Test permissions for delete user
        '''
        self.client.force_login(self.user)

        response = self.client.get(self.delete_url)

        self.assertEqual(response.status_code, 403)

    def test_user_delete_post(self):
        '''
        Test post url for delete user
        '''
        user = get_user_model().objects.create_user(
                                    first_name=self.first_name,
                                    last_name=self.last_name,
                                    username='username2',
                                    password=self.password,
        )

        delete_permission = Permission.objects.get(codename='delete_user')
        user.user_permissions.add(delete_permission)

        user.refresh_from_db()

        self.client.force_login(user)

        response = self.client.post(self.delete_url)

        self.assertEqual(response.status_code, 302)
        self.assertEqual(get_user_model().objects.all().count(), 1)

    def test_reset_password_get(self):
        '''
        Test get url for reset user's password
        '''
        permission = Permission.objects.get(codename="reset_password")
        self.user.user_permissions.add(permission)

        self.user.refresh_from_db()

        self.client.force_login(self.user)

        response = self.client.get(self.reset_password_url)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'account/password_reset.html')

    def test_reset_password_permission(self):
        '''
        Test permissions for reset staff user's password
        '''
        user = get_user_model().objects.create_user(
                                    first_name=self.first_name,
                                    last_name=self.last_name,
                                    username='username2',
                                    password=self.password,
        )

        self.client.force_login(user)

        response = self.client.get(self.reset_password_url)

        self.assertEqual(response.status_code, 403)

    def test_reset_password_post(self):
        '''
        Test post url for reset staff user's password
        '''
        user = get_user_model().objects.create_user(
                                    first_name=self.first_name,
                                    last_name=self.last_name,
                                    username='username2',
                                    password=self.password,
        )

        password_permission = Permission.objects.get(codename="reset_password")
        user.user_permissions.add(password_permission)
        user_permission = Permission.objects.get(codename="view_user")
        user.user_permissions.add(user_permission)

        user.refresh_from_db()

        self.client.force_login(user)

        password = 'AnotherPassword'

        response = self.client.post(self.reset_password_url,
                                    data={
                                        'password1': password,
                                        'password2': password
                                    })

        self.assertRedirects(response, self.details_url)

        self.user.refresh_from_db()

        self.assertTrue(self.user.check_password(password))

    def test_user_settings_get(self):
        '''
        Test get url for user settings
        '''
        self.client.force_login(self.user)

        response = self.client.get(self.settings_details_url)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'account/settings_details.html')

    def test_user_settings_permission(self):
        '''
        Test permissions for user settings
        '''
        user = get_user_model().objects.create_user(
                                    first_name=self.first_name,
                                    last_name=self.last_name,
                                    username='username2',
                                    password=self.password,
        )

        self.client.force_login(user)

        response = self.client.get(self.settings_details_url)

        self.assertEqual(response.status_code, 403)


    def test_edit_user_settings_get(self):
        '''
        Test get url for edit user settings
        '''
        self.client.force_login(self.user)

        response = self.client.get(self.settings_edit_url)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'account/settings_edit.html')

    def test_edit_user_settings_permission(self):
        '''
        Test permissions for edit user settings
        '''
        user = get_user_model().objects.create_user(
                                    first_name=self.first_name,
                                    last_name=self.last_name,
                                    username='username2',
                                    password=self.password,
        )

        self.client.force_login(user)

        response = self.client.get(self.settings_edit_url)

        self.assertEqual(response.status_code, 403)

    def test_edit_user_settings_post(self):
        '''
        Test post url for edit user settings
        '''
        self.client.force_login(self.user)

        payload = {
                    'language': 'en',
                    'paginate': 50,
                    'default_page': 'I'
            }
        response = self.client.post(self.settings_edit_url, data=payload)

        self.user.refresh_from_db()

        self.assertEqual(response.status_code, 302)
        self.assertEqual(self.user.user_settings.paginate, payload['paginate'])

    def test_user_activities_list_get(self):
        '''
        Test get to user activities page
        '''
        self.client.force_login(self.user)

        response = self.client.get(self.activities_url)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response,
                                'account/activity.html')

    def test_user_activities_list_permission_deny(self):
        '''
        Test get staff details page to another user rejected
        '''
        user = get_user_model().objects.create_user(
                                    first_name=self.first_name,
                                    last_name=self.last_name,
                                    username='username2',
                                    password=self.password,
        )

        self.client.force_login(user)

        response = self.client.get(self.activities_url)

        self.assertEqual(response.status_code, 403)

    def test_user_activities_list_permission(self):
        '''
        Test get user activities page to another user with permission
        '''
        user = get_user_model().objects.create_user(
                                    first_name=self.first_name,
                                    last_name=self.last_name,
                                    username='username2',
                                    password=self.password,
        )

        permission = Permission.objects.get(codename="view_activity")
        user.user_permissions.add(permission)

        user.refresh_from_db()

        self.client.force_login(user)

        response = self.client.get(self.activities_url)

        self.assertEqual(response.status_code, 200)

    def test_all_activities_list_get(self):
        '''
        Test get all activities list
        '''
        permission = Permission.objects.get(codename="view_activity")
        self.user.user_permissions.add(permission)

        self.user.refresh_from_db()

        self.client.force_login(self.user)

        response = self.client.get(self.all_activities_url)

        self.assertEqual(response.status_code, 200)

    def test_all_activities_list_permission_deny(self):
        '''
        Test get all activities list rejected
        '''
        self.client.force_login(self.user)

        response = self.client.get(self.all_activities_url)

        self.assertEqual(response.status_code, 403)
