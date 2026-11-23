from django.test import TestCase, RequestFactory

from account import forms
from seshat.testing import (
                        TempDirsTestCase, PASSWORD, create_user,
                        create_superuser, image_file, )


class AuthenticationFormTest(TestCase):
    '''
    Test the login form
    '''

    def setUp(self):
        self.user = create_user('john')
        self.request = RequestFactory().post('/admin/login/')

    def test_case_insensitive_username(self):
        form = forms.MyAuthenticationForm(
                    self.request, data={'username': 'JOHN', 'password': PASSWORD})
        self.assertTrue(form.is_valid())
        self.assertEqual(form.get_user(), self.user)

    def test_wrong_password(self):
        form = forms.MyAuthenticationForm(
                    self.request, data={'username': 'john', 'password': 'wrong'})
        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors['__all__'][0].count('case-sensitive'), 1)

    def test_inactive_account(self):
        self.user.is_active = False
        self.user.save()
        form = forms.MyAuthenticationForm(
                    self.request, data={'username': 'john', 'password': PASSWORD})
        self.assertFalse(form.is_valid())
        self.assertIn('not active', form.errors['__all__'][0])


class NewFormTest(TestCase):
    '''
    Test the new user form
    '''

    def data(self, **extra):
        data = {
            'first_name': 'Ann', 'last_name': 'Lee', 'username': 'AnnLee',
            'password1': PASSWORD, 'password2': PASSWORD,
            'job': 'Clerk', 'is_active': True,
        }
        data.update(extra)
        return data

    def test_valid_form_lowercases_username(self):
        form = forms.NewForm(data=self.data(), user=create_superuser())
        self.assertTrue(form.is_valid(), form.errors)
        self.assertEqual(form.save().username, 'annlee')

    def test_superuser_field_only_for_superusers(self):
        self.assertIn('is_superuser', forms.NewForm(user=create_superuser()).fields)
        self.assertNotIn('is_superuser', forms.NewForm(user=create_user()).fields)

    def test_duplicate_username(self):
        create_user('annlee')
        form = forms.NewForm(data=self.data(), user=create_superuser())
        self.assertFalse(form.is_valid())
        self.assertIn('username', form.errors)

    def test_password_mismatch(self):
        form = forms.NewForm(
                    data=self.data(password2='other-password'),
                    user=create_superuser())
        self.assertFalse(form.is_valid())
        self.assertIn('password2', form.errors)


class EditFormTest(TestCase):
    '''
    Test the edit user form
    '''

    def test_fields_for_superuser_editing_other(self):
        form = forms.EditForm(instance=create_user('bob'), user=create_superuser())
        self.assertIn('is_superuser', form.fields)
        self.assertIn('is_active', form.fields)
        self.assertNotIn('password', form.fields)

    def test_user_cannot_disable_self(self):
        user = create_user('bob')
        form = forms.EditForm(instance=user, user=user)
        self.assertNotIn('is_active', form.fields)
        self.assertNotIn('is_superuser', form.fields)

    def test_duplicate_username(self):
        create_user('taken')
        user = create_user('bob')
        form = forms.EditForm(
                    instance=user, user=create_superuser(),
                    data={'first_name': 'Bob', 'last_name': 'B',
                          'username': 'TAKEN', 'is_active': True})
        self.assertFalse(form.is_valid())
        self.assertIn('username', form.errors)

    def test_same_username_allowed(self):
        user = create_user('bob')
        form = forms.EditForm(
                    instance=user, user=create_superuser(),
                    data={'first_name': 'Bob', 'last_name': 'B',
                          'username': 'Bob', 'is_active': True})
        self.assertTrue(form.is_valid(), form.errors)


class ProfileFormTest(TestCase):
    '''
    Test the profile form
    '''

    def test_valid(self):
        form = forms.ProfileForm(
                    instance=create_user().user_profile,
                    data={'email': 'a@b.com', 'phone': '+201234567890',
                          'birthdate': '1990-01-01', 'gender': 'M'})
        self.assertTrue(form.is_valid(), form.errors)

    def test_invalid_phone(self):
        form = forms.ProfileForm(
                    instance=create_user().user_profile,
                    data={'phone': '123'})
        self.assertFalse(form.is_valid())
        self.assertIn('phone', form.errors)


class ProfilePhotoFormTest(TempDirsTestCase):
    '''
    Test the profile photo form
    '''

    def test_photo_cropped_to_200(self):
        from PIL import Image
        photo = create_user().user_photo
        form = forms.ProfilePhotoForm(
                    instance=photo,
                    data={'x': 10, 'y': 10, 'width': 300, 'height': 300},
                    files={'photo': image_file()})
        self.assertTrue(form.is_valid(), form.errors)
        saved = form.save()
        with Image.open(saved.photo.path) as image:
            self.assertEqual(image.size, (200, 200))

    def test_photo_required(self):
        form = forms.ProfilePhotoForm(instance=create_user().user_photo, data={})
        self.assertFalse(form.is_valid())


class SettingsFormTest(TestCase):
    '''
    Test the settings form
    '''

    def test_valid(self):
        form = forms.SettingsForm(
                    instance=create_user().user_settings,
                    data={'language': 'ar', 'theme': 'DA',
                          'paginate': 20, 'default_page': 'ST'})
        self.assertTrue(form.is_valid(), form.errors)

    def test_invalid_theme(self):
        form = forms.SettingsForm(
                    instance=create_user().user_settings,
                    data={'language': 'en', 'theme': 'XX',
                          'paginate': 20, 'default_page': 'IN'})
        self.assertFalse(form.is_valid())


class PasswordFormsTest(TestCase):
    '''
    Test the change and reset password forms
    '''

    def test_change_password(self):
        user = create_user()
        form = forms.ChangePasswordForm(user, data={
                    'old_password': PASSWORD,
                    'new_password1': 'Another-Password-2',
                    'new_password2': 'Another-Password-2'})
        self.assertTrue(form.is_valid(), form.errors)
        self.assertEqual(str(form.fields['old_password'].label), 'Current Password')

    def test_reset_password_mismatch(self):
        form = forms.ResetPasswordForm(create_user(), data={
                    'new_password1': 'Another-Password-2',
                    'new_password2': 'Different-Password-3'})
        self.assertFalse(form.is_valid())
