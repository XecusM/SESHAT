from django.db import models
from django.urls import reverse
from django.utils.translation import gettext_lazy as _

from x_django_app.models import XModel

from account.models import phone_regex

# Create your models here.


class VendorCompany(models.Model, XModel):
    '''
    Model for vendors' companies
    '''
    name = models.CharField(
                            verbose_name=_('Name'),
                            max_length=128,
                            unique=True,
                            blank=False,
                            null=False
    )
    description = models.CharField(
                            verbose_name=_('Description'),
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
    tax_code = models.CharField(
                            verbose_name=_('Tax code'),
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
    created_at = models.DateTimeField(
                        verbose_name=_('Created at'),
                        auto_now_add=True,
                        blank=False
    )

    class Meta:
        verbose_name = _("Vendor's company")
        verbose_name_plural = _("Vendors' companies")
        ordering = ('name', )

    def clean(self):
        '''
        Empty unique values are stored as NULL
        '''
        self.phone = self.phone or None
        self.tax_code = self.tax_code or None

    def get_absolute_url(self):
        return reverse('vendor:CompanyDetails', kwargs={'pk': self.pk})

    def get_vendors(self):
        '''
        Get all company's vendors
        '''
        return self.vendor_company.all().order_by('first_name', 'last_name')

    def get_purchase_orders(self):
        '''
        Get all purchase orders
        '''
        return self.order_company.all().order_by('-created_at')

    def can_be_deleted(self):
        '''
        A company with vendors or orders can't be deleted
        '''
        return not (self.vendor_company.exists()
                    or self.order_company.exists())

    def __str__(self):
        '''
        String representation for the record
        '''
        return self.name


class Vendor(models.Model, XModel):
    '''
    Model to store all vendor contacts
    '''
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
    created_at = models.DateTimeField(
                        verbose_name=_('Created at'),
                        auto_now_add=True,
                        blank=False
    )

    class Meta:
        verbose_name = _('Vendor')
        verbose_name_plural = _('Vendors')
        ordering = ('first_name', 'last_name')

    def clean(self):
        '''
        Empty unique values are stored as NULL
        '''
        self.email = self.email or None
        self.phone = self.phone or None

    def get_absolute_url(self):
        return reverse('vendor:VendorDetails', kwargs={'pk': self.pk})

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
        return self.full_name
