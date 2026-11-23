import os

from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.test import TestCase

from x_django_app.models import XActivity

from account import models
from seshat.testing import (
                        TempDirsTestCase, create_user, create_superuser,
                        image_file, )


class UserManagerTest(TestCase):
    '''
    Test the custom user manager
    '''

    def test_create_user(self):
        user = get_user_model().objects.create_user(
                        'NewUser', 'password-123', first_name='A', last_name='B')
        self.assertEqual(user.username, 'newuser')
        self.assertTrue(user.check_password('password-123'))
        self.assertFalse(user.is_superuser)
        self.assertTrue(user.is_active)

    def test_create_user_without_username(self):
        with self.assertRaises(ValueError):
            get_user_model().objects.create_user('', 'password-123')

    def test_create_superuser(self):
        user = create_superuser()
        self.assertTrue(user.is_superuser)
        self.assertTrue(user.is_staff)

    def test_create_superuser_must_be_superuser(self):
        with self.assertRaises(ValueError):
            get_user_model().objects.create_superuser(
                                'admin', 'password-123', is_superuser=False)


class UserModelTest(TestCase):
    '''
    Test the user model
    '''

    def setUp(self):
        self.user = create_user('john', first_name='John', last_name='Smith')

    def test_str_and_full_name(self):
        self.assertEqual(str(self.user), 'john')
        self.assertEqual(self.user.full_name, 'John Smith')

    def test_clean_lowercases_username(self):
        self.user.username = 'JOHN'
        self.user.clean()
        self.assertEqual(self.user.username, 'john')

    def test_related_records_created(self):
        self.assertIsInstance(self.user.user_profile, models.Profile)
        self.assertIsInstance(self.user.user_photo, models.ProfilePhoto)
        self.assertIsInstance(self.user.user_settings, models.Settings)

    def test_custom_permissions(self):
        codenames = [codename for codename, _ in get_user_model()._meta.permissions]
        for codename in ['reset_password', 'import', 'export', 'backup',
                         'restore', 'view_activity', 'report_activity']:
            self.assertIn(codename, codenames)

    def test_get_activities(self):
        admin = create_superuser()
        XActivity.objects.create_activity(
                activity_object=self.user, activity=XActivity.EDIT,
                user=admin, message='Account-john')
        self.assertEqual(self.user.get_activities().count(), 1)


class ProfileModelTest(TestCase):
    '''
    Test the profile model
    '''

    def setUp(self):
        self.profile = create_user('mary').user_profile

    def test_str(self):
        self.assertEqual(str(self.profile), 'mary')

    def test_clean_normalizes_email_and_blanks(self):
        self.profile.email = 'Mary@EXAMPLE.com'
        self.profile.phone = ''
        self.profile.clean()
        self.assertEqual(self.profile.email, 'Mary@example.com')
        self.assertIsNone(self.profile.phone)

    def test_clean_empty_email(self):
        self.profile.email = ''
        self.profile.clean()
        self.assertIsNone(self.profile.email)

    def test_phone_validator(self):
        self.profile.phone = 'not-a-phone'
        with self.assertRaises(ValidationError):
            self.profile.full_clean()


class SettingsModelTest(TestCase):
    '''
    Test the user settings model
    '''

    def setUp(self):
        self.settings = create_user('sam').user_settings

    def test_defaults(self):
        self.assertEqual(self.settings.language, models.Settings.ENGLISH)
        self.assertEqual(self.settings.theme, models.Settings.AUTO)
        self.assertEqual(self.settings.paginate, 30)
        self.assertEqual(self.settings.default_page, models.Settings.INDEX)
        self.assertEqual(str(self.settings), 'sam')

    def test_theme_names(self):
        for theme, name in [(models.Settings.AUTO, 'auto'),
                            (models.Settings.LIGHT, 'light'),
                            (models.Settings.DARK, 'dark')]:
            self.settings.theme = theme
            self.assertEqual(self.settings.get_theme_name(), name)

    def test_paginate_limits(self):
        self.settings.paginate = 1
        with self.assertRaises(ValidationError):
            self.settings.full_clean()


class ProfilePhotoModelTest(TempDirsTestCase):
    '''
    Test the profile photo model and its file signals
    '''

    def setUp(self):
        self.user = create_user('pat')
        self.photo = self.user.user_photo

    def test_str(self):
        self.assertEqual(str(self.photo), 'pat')

    def test_upload_path(self):
        path = models.get_image_path(self.photo, 'me.jpg')
        self.assertTrue(path.startswith(f'profiles/{self.user.id}/'))
        self.assertTrue(path.endswith('.jpg'))

    def test_old_file_removed_on_change_and_delete(self):
        self.photo.photo = image_file('first.png')
        self.photo.save()
        first_path = self.photo.photo.path
        self.assertTrue(os.path.isfile(first_path))

        self.photo.photo = image_file('second.png')
        self.photo.save()
        self.assertFalse(os.path.isfile(first_path))

        second_path = self.photo.photo.path
        self.photo.delete()
        self.assertFalse(os.path.isfile(second_path))
