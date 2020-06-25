from django.db import models
from django.contrib.auth.models import (AbstractBaseUser,
                                        PermissionsMixin,
                                        BaseUserManager)
from django.contrib.auth.models import Permission
from django.utils.translation import ugettext_lazy as _
from django.core.validators import RegexValidator
from django.dispatch import receiver

import uuid
import os

# Help Functions

def get_image_path(instance, filename):
    '''
    Uploading image function
    '''
    ext = filename.split('.')[-1]
    filename = f'{uuid.uuid4()}.{ext}'

    return os.path.join(f'profiles/{instance.user.pk}/', filename)


# Create your models here.


class UserManager(BaseUserManager):
    '''
    Helps Django work with our custom user model.
    '''
    use_in_migrations = True

    def _create_user(self, username, password, **extra_fields):
        """
        Creates and saves a User with the given username and password.
        """

        user = self.model(username=username, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, username, password=None, **extra_fields):
        extra_fields.setdefault('is_superuser', False)
        extra_fields.setdefault('is_staff', False)
        return self._create_user(username, password, **extra_fields)

    def create_superuser(self, username, password, **extra_fields):
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_staff', True)

        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser = True.')

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff = True.')

        return self._create_user(username, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    '''
    This a replaced user profile instead of the default django one
    '''
    username = models.CharField(
                            verbose_name=_('Username'),
                            max_length=128,
                            unique=True,
                            blank=False,
                            null=False
    )
    first_name = models.CharField(
                            verbose_name=_('First Name'),
                            max_length=128,
                            unique=False,
                            blank=False,
                            null=False
    )
    last_name = models.CharField(
                            verbose_name=_('Last Name'),
                            max_length=128,
                            unique=False,
                            blank=False,
                            null=False
    )
    job = models.CharField(
                            verbose_name=_('Job'),
                            max_length=256,
                            unique=False,
                            blank=True,
                            null=True
    )
    is_superuser = models.BooleanField(
                            verbose_name=_('Admin'),
                            default=False
    )
    is_active = models.BooleanField(
                            verbose_name=_('Enabled'),
                            default=True
    )
    is_staff = models.BooleanField(
                            verbose_name=_('IT'),
                            default=False
    )
    created_at = models.DateTimeField(
                            verbose_name=_('Joined at'),
                            auto_now_add=True,
                            blank=False
    )

    objects = UserManager()

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['first_name', 'last_name']

    def clean(self):
        '''
        Change cleaed data before save to datase
        '''
        self.username = self.username.lower()

    @property
    def full_name(self):
        '''
        Used to get users full name.
        '''
        return f'{self.first_name} {self.last_name}'

    class Meta:
        permissions = (
                        ("reset_password", "Can reset user's password"),
                        ("import", "Can import data"),
                        ("export", "Can export data"),
                        ("backup", "Can backup database"),
                        ("restore", "Can restore database"),

                        )

    def __str__(self):
        '''
        Django uses this when it needs to convert the object to a string.
        '''
        return self.username


class UserProfile(models.Model):
    '''
    This a user profile for users' accounts
    '''
    #########################################
    # Choices
    MALE = 'M'
    FEMALE = 'F'
    gender_choices = [
                    (MALE, _('Male')),
                    (FEMALE, _('Female'))
    ]
    #########################################
    phone_regex = RegexValidator(
            regex=r'^\+?1?\d{9,15}$',
            message=_("Phone number must be entered in the \
                        format: '+999999999'. Up to 15 digits allowed."))

    user = models.OneToOneField(
                        'User',
                        related_name='user_profile',
                        verbose_name=_('User'),
                        on_delete=models.CASCADE,
                        blank=False,
                        null=False
    )
    email = models.EmailField(
                            verbose_name=_('Email'),
                            max_length=256,
                            unique=True,
                            blank=True,
                            null=True
    )
    phone = models.CharField(
                            verbose_name=_('Phone'),
                            validators=[phone_regex],
                            max_length=17,
                            unique=True,
                            blank=True,
                            null=True
    )
    birthdate = models.DateField(
                            verbose_name=_('Birthdate'),
                            max_length=25,
                            unique=False,
                            blank=True,
                            null=True
    )
    gender = models.CharField(
                            verbose_name=_('Gender'),
                            max_length=1,
                            choices=gender_choices,
                            blank=True,
                            null=True
    )
    photo = models.ImageField(
                            verbose_name=_('Profile Picture'),
                            upload_to=get_image_path,
                            null=True,
                            blank=True
    )

    def clean(self):
        '''
        Change cleaed data before save to datase
        '''
        self.email = BaseUserManager.normalize_email(self.email)

    def __str__(self):
        '''
        String representation for the record
        '''
        return self.user.username


class UserSettings(models.Model):
    '''
    This a user settings for users' accounts
    '''
    #########################################
    # Language choices
    ENGLISH = 'en'
    ARABIC = 'ar'
    language_choices=[
                    (ENGLISH, _('English')),
                    (ARABIC, _('Arabic'))
    ]
    # Page choices
    INDEX = 'I'
    ADMIN = 'A'
    STOCK = 'T'
    CUSTOMER = 'C'
    VENDOR = 'V'
    PURCHASE = 'P'
    SALE = 'S'
    page_choices=[
                    (INDEX, _('Dashboard')),
                    (ADMIN, _('Admin')),
                    (STOCK, _('Stock')),
                    (CUSTOMER, _('Customers')),
                    (VENDOR, _('Vendors')),
                    (PURCHASE, _('Purchases')),
                    (SALE, _('Sales')),
    ]
    #########################################
    user = models.OneToOneField(
                        'User',
                        related_name='user_settings',
                        verbose_name=_('User'),
                        on_delete=models.CASCADE,
                        blank=False,
                        null=False
    )
    language = models.CharField(
                        verbose_name=_('Language'),
                        max_length=2,
                        choices=language_choices,
                        default=ENGLISH
    )
    paginate = models.IntegerField(
                        verbose_name=_('Page Limit'),
                        unique=False,
                        blank=False,
                        null=False,
                        default=30
    )
    default_page = models.CharField(
                        verbose_name=_('Language'),
                        max_length=1,
                        choices=page_choices,
                        default=INDEX
    )

    def __str__(self):
        '''
        String representation for the record
        '''
        return self.user.username


# Signals
@receiver(models.signals.post_save, sender=User)
def create_new_settings(sender, instance, **kwargs):
    '''
    Create a new object on new user acccount
    '''
    UserProfile.objects.get_or_create(user=instance)
    UserSettings.objects.get_or_create(user=instance)


@receiver(models.signals.post_delete, sender=UserProfile)
def auto_delete_file_on_delete(sender, instance, **kwargs):
    """
    Deletes file from filesystem
    when corresponding `UserProfile` object is deleted.
    """
    if instance.photo and os.path.isfile(instance.photo.path):
        os.remove(instance.photo.path)


@receiver(models.signals.pre_save, sender=UserProfile)
def auto_delete_file_on_change(sender, instance, **kwargs):
    """
    Deletes old file from filesystem
    when corresponding `UserProfile` object is updated
    with new file.
    """
    if instance.pk:
        old_photo = UserProfile.objects.get(pk=instance.pk).photo
        new_photo = instance.photo
        if not old_photo == new_photo and old_photo and \
            os.path.isfile(old_photo.path):
            os.remove(old_photo.path)
