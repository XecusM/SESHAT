from django.db import models
from django.urls import reverse
from django.utils.translation import gettext_lazy as _

from x_django_app.models import XModel

from account.models import phone_regex

# Create your models here.


class CustomerCompany(models.Model, XModel):
    '''
    Model for customers' companies
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
        verbose_name = _("Customer's company")
        verbose_name_plural = _("Customers' companies")
        ordering = ('name', )

    def clean(self):
        '''
        Empty unique values are stored as NULL
        '''
        self.phone = self.phone or None
        self.tax_code = self.tax_code or None

    def get_absolute_url(self):
        return reverse('customer:CompanyDetails', kwargs={'pk': self.pk})

    def get_customers(self):
        '''
        Get all company's customers
        '''
        return self.customer_company.all().order_by('first_name', 'last_name')

    def get_sale_orders(self):
        '''
        Get all sale orders
        '''
        return self.order_company.all().order_by('-created_at')

    def can_be_deleted(self):
        '''
        A company with customers or orders can't be deleted
        '''
        return not (self.customer_company.exists()
                    or self.order_company.exists())

    def __str__(self):
        '''
        String representation for the record
        '''
        return self.name


class Customer(models.Model, XModel):
    '''
    Model to store all customer contacts
    '''
    company = models.ForeignKey(
                        'CustomerCompany',
                        verbose_name=_('Company'),
                        related_name='customer_company',
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
        verbose_name = _('Customer')
        verbose_name_plural = _('Customers')
        ordering = ('first_name', 'last_name')

    def clean(self):
        '''
        Empty unique values are stored as NULL
        '''
        self.email = self.email or None
        self.phone = self.phone or None

    def get_absolute_url(self):
        return reverse('customer:CustomerDetails', kwargs={'pk': self.pk})

    @property
    def full_name(self):
        '''
        Used to get customers full name.
        '''
        return f'{self.first_name} {self.last_name}'

    def __str__(self):
        '''
        String representation for the record
        '''
        return self.full_name
