from django import forms
from django.utils.translation import gettext_lazy as _

from . import models


class CompanyForm(forms.ModelForm):
    '''
    Form for customer's company
    '''
    class Meta:
        model = models.CustomerCompany
        fields = [
                    'name', 'description', 'phone', 'website',
                    'tax_code', 'note',
        ]
        widgets = {
            'note': forms.Textarea(attrs={'rows': 3}),
        }

    def __init__(self, *args, **kwargs):
        '''
        Method for initial values and functions
        '''
        super().__init__(*args, **kwargs)
        self.fields['name'].widget.attrs['placeholder'] = _('Company name')
        self.fields['description'].widget.attrs['placeholder'] = _(
                                                    'Company description')
        self.fields['phone'].widget.attrs['placeholder'] = _('+999999999')
        self.fields['phone'].help_text = _(
                            "format: '+999999999'. Up to 15 digits allowed")
        self.fields['website'].widget.attrs['placeholder'] = _(
                                                'https://www.example.com/')
        self.fields['tax_code'].widget.attrs['placeholder'] = _(
                                                "Company's tax code")


class CustomerForm(forms.ModelForm):
    '''
    Form for customer
    '''
    class Meta:
        model = models.Customer
        fields = [
                    'company', 'first_name', 'last_name', 'email',
                    'phone', 'department', 'job', 'note',
        ]
        widgets = {
            'note': forms.Textarea(attrs={'rows': 3}),
        }

    def __init__(self, *args, **kwargs):
        '''
        Method for initial values and functions
        '''
        super().__init__(*args, **kwargs)
        self.fields['company'].help_text = _("Select company")
        self.fields['first_name'].widget.attrs['placeholder'] = _('First name')
        self.fields['last_name'].widget.attrs['placeholder'] = _('Last name')
        self.fields['phone'].widget.attrs['placeholder'] = _('+999999999')
        self.fields['phone'].help_text = _(
                            "format: '+999999999'. Up to 15 digits allowed")
        self.fields['email'].widget.attrs['placeholder'] = _('Email address')
        self.fields['department'].widget.attrs['placeholder'] = _("Department")
        self.fields['job'].widget.attrs['placeholder'] = _("Job title")
