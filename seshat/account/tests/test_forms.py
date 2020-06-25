from django.test import TestCase
from django.contrib.auth import get_user_model

from account import forms, models


class AccountFormsTests(TestCase):
    '''
    Test all forms for account appliction
    '''
    def setUp(self):
        '''
        Initial setup for ever test
        '''
        self.first_name = 'Mohamed'
        self.last_name = 'Aboel-fotouh'
        self.password = 'Testpassword'

        self.superuser = get_user_model().objects.create_user(
                                username='xecus',
                                first_name=self.first_name,
                                last_name=self.last_name,
                                password=self.password,
                                is_active=True,
                                is_superuser=True
        )

        self.user = get_user_model().objects.create_user(
                                username='usename',
                                first_name=self.first_name,
                                last_name=self.last_name,
                                password=self.password,
                                is_active=True,
        )

    def test_new_account_form_fields(self):
        '''
        Test user new account form fields
        '''
        expected = [
                    'first_name', 'last_name', 'username',
                    'password1', 'password2', 'job',
                    'is_superuser', 'is_active'
            ]

        actual = list(forms.NewForm(user=self.superuser).fields)
        self.assertSequenceEqual(expected, actual)

    def test_new_account_form_valid_data(self):
        '''
        Test valid form for creating new account user
        '''
        form = forms.NewForm(data={
                                'username': 'another_user',
                                'first_name': 'Mohamed',
                                'last_name': 'Aboel-fotouh',
                                'password1': self.password,
                                'password2': self.password,
                            }, user=self.superuser)

        self.assertTrue(form.is_valid())

    def test_new_account_form_invalid_data(self):
        '''
        Test invalid form senarios for creating new account user
        '''
        form_username = forms.NewForm(data={
                                'username': '',
                                'first_name': 'Mohamed',
                                'last_name': 'Aboel-fotouh',
                                'password1': self.password,
                                'password2': self.password,
                            }, user=self.superuser)

        form_first_name = forms.NewForm(data={
                                'username': 'xecus',
                                'first_name': '',
                                'last_name': 'Aboel-fotouh',
                                'password1': self.password,
                                'password2': self.password,
                            }, user=self.superuser)

        form_last_name = forms.NewForm(data={
                                'username': 'another_user',
                                'first_name': 'Mohamed',
                                'last_name': '',
                                'password1': self.password,
                                'password2': self.password,
                            }, user=self.superuser)

        self.assertFalse(form_username.is_valid())
        self.assertFalse(form_first_name.is_valid())
        self.assertFalse(form_last_name.is_valid())

    def test_edit_account_form_fields(self):
        '''
        Test edit account user form fields
        '''
        expected = [
                    'first_name', 'last_name','username',
                    'job', 'is_superuser', 'is_active'
            ]

        actual = list(forms.EditForm(
                                    instance=self.user, user=self.superuser
                                    ).fields)

        self.assertSequenceEqual(expected, actual)

    def test_edit_account_form_valid_data(self):
        '''
        Test valid form for edit account user details
        '''
        form = forms.EditForm(data={
                                'username': 'another_user',
                                'first_name': 'Mohamed',
                                'last_name': 'Aboel-fotouh',
                            },
                            instance=self.user, user=self.superuser)
        self.assertTrue(form.is_valid())

    def test_edit_account_form_invalid_data(self):
        '''
        Test invalid form senarios for edit account user details
        '''
        form_username = forms.EditForm(data={
                                'username': '',
                                'first_name': 'Mohamed',
                                'last_name': 'Aboel-fotouh',
                            },
                            instance=self.user, user=self.superuser)

        form_first_name = forms.EditForm(data={
                                'username': 'another_user',
                                'first_name': '',
                                'last_name': 'Aboel-fotouh',
                            },
                            instance=self.user, user=self.superuser)

        form_last_name = forms.EditForm(data={
                                'username': 'another_user',
                                'first_name': 'Mohamed',
                                'last_name': '',
                            },
                            instance=self.user, user=self.superuser)

        self.assertFalse(form_username.is_valid())
        self.assertFalse(form_first_name.is_valid())
        self.assertFalse(form_last_name.is_valid())

    def test_user_profile_form_fields(self):
        '''
        Test user profile form fields
        '''
        expected = [
                    'photo', 'email', 'phone', 'birthdate', 'gender',
                    'x', 'y', 'width', 'height',
                ]

        actual = list(forms.ProfileForm().fields)

        self.assertSequenceEqual(expected, actual)

    def test_user_profile_form_valid_data(self):
        '''
        Test valid form for user profile
        '''
        form = forms.ProfileForm(data={
                                'email': 'user@email.com',
                                'phone': '+999988888',
                                'birthdate': '1982-5-24',
                                'gender': models.UserProfile.MALE,
                            })

        self.assertTrue(form.is_valid())

    def test_user_profile_form_invalid_data(self):
        '''
        Test invalid form senarios for user profile
        '''
        form_email = forms.ProfileForm(data={
                                'email': 'user-email.com',
                                'phone': '+999988888',
                                'birthdate': '1982-5-24',
                                'gender': models.UserProfile.MALE,
                            })

        form_phone = forms.ProfileForm(data={
                                'email': 'user@email.com',
                                'phone': 'error',
                                'birthdate': '1982-5-24',
                                'gender': models.UserProfile.MALE,
                            })

        form_birthdate = forms.ProfileForm(data={
                                'email': 'user@email.com',
                                'phone': '+999988888',
                                'birthdate': '15/10/12',
                                'gender': models.UserProfile.MALE,
                            })

        self.assertFalse(form_email.is_valid())
        self.assertFalse(form_phone.is_valid())
        self.assertFalse(form_birthdate.is_valid())

    def test_user_settings_form_fields(self):
        '''
        Test user settings form fields
        '''
        expected = ['language', 'paginate', 'default_page', ]

        actual = list(forms.SettingsForm().fields)

        self.assertSequenceEqual(expected, actual)

    def test_user_settings_form_valid_data(self):
        '''
        Test valid form for user settings
        '''
        form = forms.SettingsForm(data={
                                'language': models.UserSettings.ENGLISH,
                                'paginate': 30,
                                'default_page': models.UserSettings.ADMIN,
                            })
        self.assertTrue(form.is_valid())

    def test_user_settings_form_invalid_data(self):
        '''
        Test invalid form senarios for user settings
        '''
        form_language = forms.SettingsForm(data={
                                'language': '',
                                'paginate': 30,
                                'default_page': models.UserSettings.ADMIN,
                            })

        form_paginate = forms.SettingsForm(data={
                                'language': models.UserSettings.ENGLISH,
                                'paginate': '',
                                'default_page': models.UserSettings.ADMIN,
                            })

        form_page = forms.SettingsForm(data={
                                'language': models.UserSettings.ENGLISH,
                                'paginate': 30,
                                'default_page': '',
                            })

        self.assertFalse(form_language.is_valid())
        self.assertFalse(form_paginate.is_valid())
        self.assertFalse(form_page.is_valid())
