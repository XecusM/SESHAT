from django.test import TestCase

from django.contrib.auth import get_user_model

from account import models


class AccountModelsTests(TestCase):
    '''
    Test all models for account applications
    '''
    def test_create_new_superuser(self):
        '''
        Test creating a new super user account
        '''
        superuser = get_user_model().objects.create_superuser(
                                        username='xecus',
                                        first_name='Mohamed',
                                        last_name='Aboel-fotouh',
                                        password='Testpass123',)

        self.assertEqual(get_user_model().objects.all().count(), 1)
        self.assertTrue(superuser.is_superuser)
        self.assertTrue(superuser.is_staff)
        self.assertTrue(superuser.is_active)

    def test_create_new_user(self):
        '''
        Test creating a new user account
        '''
        user = get_user_model().objects.create_user(
                                        username='xecus',
                                        first_name='Mohamed',
                                        last_name='Aboel-fotouh',
                                        password='Testpass123',)

        self.assertEqual(get_user_model().objects.all().count(), 1)
        self.assertFalse(user.is_superuser)
        self.assertFalse(user.is_staff)
        self.assertTrue(user.is_active)

    def test_full_name(self):
        '''
        Test full_name method in Customer model
        '''
        first_name = 'Mohamed'
        last_name = 'Aboel-fotouh'
        user = get_user_model().objects.create_user(
                                        username='xecus',
                                        first_name=first_name,
                                        last_name=last_name,
                                        password='Testpass123',)

        self.assertEqual(user.full_name, f'{first_name} {last_name}')

    def test_create_user_profile(self):
        '''
        Test creating a new user profile
        '''
        get_user_model().objects.create_user(
                                        username='xecus',
                                        first_name='Mohamed',
                                        last_name='Aboel-fotouh',
                                        password='Testpass123',)

        self.assertEqual(models.UserProfile.objects.all().count(), 1)

    def test_create_user_settings(self):
        '''
        Test creating a new user settings
        '''
        get_user_model().objects.create_user(
                                        username='xecus',
                                        first_name='Mohamed',
                                        last_name='Aboel-fotouh',
                                        password='Testpass123',)

        self.assertEqual(models.UserSettings.objects.all().count(), 1)
