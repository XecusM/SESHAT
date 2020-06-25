from django import forms
from django.utils.translation import ugettext_lazy as _

from . import models


class CompanyForm(forms.ModelForm):
    '''
    Form for customer's company
    '''
    class Meta:
        model = models.VendorCompany
        fields = [
                    'name', 'desciption', 'phone', 'website', 'taxs_code'
        ]

    def __init__(self, *args, **kwargs):
        '''
        Method for initial values and functions
        '''
        # get the initial form class values
        super().__init__(*args, **kwargs)
        # initate is_active
        self.fields['name'].widget.attrs['placeholder'] = _('Company name')
        self.fields['desciption'].widget.attrs['placeholder'] = _(
                                                        'Company desciption')
        self.fields['phone'].widget.attrs['placeholder'] = _('+999999999')
        self.fields['phone'].help_text = _(
                            "format: '+999999999'. Up to 15 digits allowed")
        self.fields['website'].widget.attrs['placeholder'] = _(
                                                'https://www.example.com/')
        self.fields['website'].help_text = _(
                            "Company website i.e. https://www.example.com/")
        self.fields['taxs_code'].widget.attrs['placeholder'] = _(
                                                        "Company tax's code")


class VendorForm(forms.ModelForm):
    '''
    Form for vendor
    '''
    class Meta:
        model = models.Vendor
        fields = [
                    'company', 'first_name', 'last_name', 'email',
                    'phone', 'department', 'job'
        ]

    def __init__(self, *args, **kwargs):
        '''
        Method for initial values and functions
        '''
        # get the initial form class values
        super().__init__(*args, **kwargs)
        # initate is_active
        self.fields['company'].help_text = _("Select company")
        self.fields['first_name'].widget.attrs['placeholder'] = _('Enter name')
        self.fields['last_name'].widget.attrs['placeholder'] = _('Enter name')
        self.fields['phone'].widget.attrs['placeholder'] = _('+999999999')
        self.fields['phone'].help_text = _(
                            "format: '+999999999'. Up to 15 digits allowed")
        self.fields['email'].widget.attrs['placeholder'] = _('email address')
        self.fields['email'].help_text = _("i.e. name@email.com")
        self.fields['department'].widget.attrs['placeholder'] = _("Department")
        self.fields['job'].widget.attrs['placeholder'] = _("Job title")
