from django.db import models
from django.contrib.auth.models import (AbstractBaseUser,
                                        PermissionsMixin,
                                        BaseUserManager)
from django.utils.translation import gettext_lazy as _
from django.core.validators import RegexValidator, MinValueValidator, MaxValueValidator
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

    return os.path.join(f'profiles/{instance.user.id}/', filename)


phone_regex = RegexValidator(
        regex=r'^\+?1?\d{9,15}$',
        message=_("Phone number must be entered in the format: "
                  "'+999999999'. Up to 15 digits allowed."))


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
        if not username:
            raise ValueError('The username must be set.')
        user = self.model(username=str(username).lower(), **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, username, password=None, **extra_fields):
        extra_fields.setdefault('is_superuser', False)
        return self._create_user(username, password, **extra_fields)

    def create_superuser(self, username, password, **extra_fields):
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser = True.')

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
                            verbose_name=_('Job Position'),
                            max_length=256,
                            unique=False,
                            blank=True,
                            null=True
    )
    is_superuser = models.BooleanField(
                            verbose_name=_('Administrator'),
                            default=False
    )
    is_active = models.BooleanField(
                            verbose_name=_('Enabled'),
                            default=True
    )
    created_at = models.DateTimeField(
                            verbose_name=_('Joined at'),
                            auto_now_add=True,
                            blank=False
    )

    objects = UserManager()

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['first_name', 'last_name']

    class Meta:
        verbose_name = _('User')
        verbose_name_plural = _('Users')
        permissions = (
                        ("reset_password", "Can reset user's password"),
                        ("import", "Can import data"),
                        ("export", "Can export data"),
                        ("backup", "Can backup database"),
                        ("restore", "Can restore database"),
                        ("view_activity", "Can view user activity"),
                        ("report_activity", "Can view user activity report"),
        )

    def clean(self):
        '''
        Change cleaned data before save to database
        '''
        super().clean()
        self.username = str(self.username).lower()

    @property
    def is_staff(self):
        '''
        Kept for compatibility with Django's contrib apps
        '''
        return self.is_superuser

    def get_activities(self):
        '''
        Get the activities recorded on this account (x_django_app imports
        the user model, so XModel can't be used here)
        '''
        from django.contrib.contenttypes.models import ContentType
        from x_django_app.models import XActivity
        return XActivity.objects.filter(
                        activity_type=ContentType.objects.get_for_model(self),
                        activity_id=self.pk).order_by('-created_at')

    @property
    def full_name(self):
        '''
        Used to get users full name.
        '''
        return f'{self.first_name} {self.last_name}'

    def __str__(self):
        '''
        Django uses this when it needs to convert the object to a string.
        '''
        return self.username


class Profile(models.Model):
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

    def clean(self):
        '''
        Change cleaned data before save to database
        '''
        if self.email:
            self.email = BaseUserManager.normalize_email(self.email)
        else:
            self.email = None
        if not self.phone:
            self.phone = None

    def __str__(self):
        '''
        String representation for the record
        '''
        return self.user.username


class ProfilePhoto(models.Model):
    '''
    Model for profile photo
    '''
    user = models.OneToOneField(
                            User,
                            on_delete=models.CASCADE,
                            related_name='user_photo',
                            verbose_name=_('User'),
                            blank=False,
                            null=False
    )
    photo = models.ImageField(
                            verbose_name=_('Profile Picture'),
                            help_text=_('*image must be more than 200x200'),
                            upload_to=get_image_path,
                            blank=True,
                            null=False
    )
    created_at = models.DateTimeField(
                            verbose_name=_('Created at'),
                            auto_now_add=True,
                            blank=False
    )

    def __str__(self):
        '''
        String representation for the record
        '''
        return self.user.username


class Settings(models.Model):
    '''
    This a user settings for users' accounts
    '''
    #########################################
    # Language choices
    ENGLISH = 'en'
    ARABIC = 'ar'
    language_choices = [
                    (ENGLISH, _('English')),
                    (ARABIC, _('Arabic'))
    ]
    # Theme choices
    AUTO = 'AU'
    LIGHT = 'LI'
    DARK = 'DA'
    theme_choices = [
                    (AUTO, _('Auto (follow system)')),
                    (LIGHT, _('Light')),
                    (DARK, _('Dark'))
    ]
    theme_names = {AUTO: 'auto', LIGHT: 'light', DARK: 'dark'}
    # Page choices
    INDEX = 'IN'
    ADMIN = 'AD'
    STOCK = 'ST'
    CUSTOMER = 'CU'
    VENDOR = 'VE'
    PURCHASE = 'PU'
    SALE = 'SA'
    page_choices = [
                    (INDEX, _('Dashboard')),
                    (ADMIN, _('Administration')),
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
    theme = models.CharField(
                        verbose_name=_('Theme'),
                        max_length=2,
                        choices=theme_choices,
                        default=AUTO
    )
    paginate = models.IntegerField(
                        verbose_name=_('Page Limit'),
                        validators=[MinValueValidator(5), MaxValueValidator(500)],
                        unique=False,
                        blank=False,
                        null=False,
                        default=30
    )
    default_page = models.CharField(
                        verbose_name=_('Default Page'),
                        max_length=2,
                        choices=page_choices,
                        default=INDEX
    )

    def get_theme_name(self):
        '''
        Return the theme name used by the templates
        '''
        return self.theme_names.get(self.theme, 'auto')

    def __str__(self):
        '''
        String representation for the record
        '''
        return self.user.username


# Signals
@receiver(models.signals.post_save, sender=User)
def create_new_settings(sender, instance, raw=False, **kwargs):
    '''
    Create the related records for a new user account
    '''
    if raw:
        return
    Profile.objects.get_or_create(user=instance)
    ProfilePhoto.objects.get_or_create(user=instance)
    Settings.objects.get_or_create(user=instance)


@receiver(models.signals.post_delete, sender=ProfilePhoto)
def auto_delete_file_on_delete(sender, instance, **kwargs):
    """
    Deletes file from filesystem
    when corresponding `Profile Photo` object is deleted.
    """
    if instance.photo and os.path.isfile(instance.photo.path):
        os.remove(instance.photo.path)


@receiver(models.signals.pre_save, sender=ProfilePhoto)
def auto_delete_file_on_change(sender, instance, raw=False, **kwargs):
    """
    Deletes old file from filesystem
    when corresponding `Profile Photo` object is updated
    with new file.
    """
    if raw or not instance.pk:
        return
    try:
        old_photo = sender.objects.get(pk=instance.pk).photo
    except sender.DoesNotExist:
        return
    new_photo = instance.photo
    if not old_photo == new_photo and old_photo and \
            os.path.isfile(old_photo.path):
        os.remove(old_photo.path)
