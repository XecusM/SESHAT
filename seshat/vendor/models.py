from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.core.validators import RegexValidator
from django.utils.translation import ugettext_lazy as _
# Create your models here.


class VendorCompany(models.Model):
    '''
    Model for vendor's companies
    '''
    phone_regex = RegexValidator(
            regex=r'^\+?1?\d{9,15}$',
            message=_("Phone number must be entered in the \
                        format: '+999999999'. Up to 15 digits allowed."))

    name = models.CharField(
                            verbose_name=_('Name'),
                            max_length=128,
                            unique=True,
                            blank=False,
                            null=False
    )
    desciption = models.CharField(
                            verbose_name=_('Desciption'),
                            max_length=255,
                            unique=False,
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
    website = models.URLField(
                            verbose_name=_('Website'),
                            max_length=255,
                            unique=False,
                            blank=True,
                            null=True
    )
    taxs_code = models.CharField(
                            verbose_name=_('Taxs code'),
                            max_length=128,
                            unique=True,
                            blank=True,
                            null=True
    )
    note = models.TextField(
                            verbose_name=_('Notes'),
                            max_length=255,
                            unique=False,
                            blank=True,
                            null=True
    )
    edited_at = models.DateTimeField(
                        verbose_name=_('Edited at'),
                        null=True,
                        blank=True
    )
    edited_by = models.ForeignKey(
                        get_user_model(),
                        verbose_name=_('Edited by'),
                        related_name='company_vendor_user_edit',
                        on_delete=models.PROTECT,
                        blank=True,
                        null=True
    )
    created_at = models.DateTimeField(
                        verbose_name=_('Created at'),
                        auto_now_add=True,
                        blank=False
    )
    created_by = models.ForeignKey(
                        get_user_model(),
                        verbose_name=_('Created by'),
                        related_name='company_vendor_user_create',
                        on_delete=models.PROTECT,
                        blank=True,
                        null=True
    )

    def edited(self, user):
        '''
        Edit Company
        '''
        self.edited_at = timezone.now()
        self.edited_by = user
        self.save()

    def get_vendors(self):
        '''
        Get all company's vendors
        '''
        return self.vendor_company.filter(company=self.id).order_by(
                                                    'first_name', 'last_name')

    def __str__(self):
        '''
        String representation for the record
        '''
        return self.name


class Vendor(models.Model):
    '''
    Model to store all vendor data
    '''
    phone_regex = RegexValidator(
            regex=r'^\+?1?\d{9,15}$',
            message=_("Phone number must be entered in the \
                        format: '+999999999'. Up to 15 digits allowed."))

    company = models.ForeignKey(
                        'VendorCompany',
                        verbose_name=_('Company'),
                        related_name='vendor_company',
                        on_delete=models.PROTECT,
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
    department = models.CharField(
                            verbose_name=_('Department'),
                            max_length=256,
                            unique=False,
                            blank=True,
                            null=True
    )
    job = models.CharField(
                            verbose_name=_('Job'),
                            max_length=256,
                            unique=False,
                            blank=True,
                            null=True
    )
    note = models.TextField(
                            verbose_name=_('Notes'),
                            max_length=255,
                            unique=False,
                            blank=True,
                            null=True
    )
    edited_at = models.DateTimeField(
                        verbose_name=_('Edited at'),
                        null=True,
                        blank=True
    )
    edited_by = models.ForeignKey(
                        get_user_model(),
                        verbose_name=_('Edited by'),
                        related_name='vendor_user_edit',
                        on_delete=models.PROTECT,
                        blank=True,
                        null=True
    )
    created_at = models.DateTimeField(
                        verbose_name=_('Created at'),
                        auto_now_add=True,
                        blank=False
    )
    created_by = models.ForeignKey(
                        get_user_model(),
                        verbose_name=_('Created by'),
                        related_name='vendor_user_create',
                        on_delete=models.PROTECT,
                        blank=True,
                        null=True
    )

    def edited(self, user):
        '''
        Edit Company
        '''
        self.edited_at = timezone.now()
        self.edited_by = user
        self.save()

    @property
    def full_name(self):
        '''
        Used to get vendors full name.
        '''
        return f'{self.first_name} {self.last_name}'

    def __str__(self):
        '''
        String representation for the record
        '''
        return f"{self.first_name} {self.last_name}"
