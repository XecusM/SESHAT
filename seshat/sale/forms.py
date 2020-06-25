from django import forms
from django.utils.translation import ugettext_lazy as _

from . import models


class OrderForm(forms.ModelForm):
    '''
    Form for order
    '''
    class Meta:
        model = models.SaleOrder
        fields = ['company', 'invoice', 'invoice_date', 'note', ]

        widgets = {
            'invoice_date': forms.TextInput(attrs={'type': 'date'}),
        }

    def __init__(self, *args, **kwargs):
        '''
        Method for initial values and functions
        '''
        # get the initial form class values
        super().__init__(*args, **kwargs)
        # initate is_active
        self.fields['company'].help_text = _("Select company")
        self.fields['invoice'].widget.attrs[
                                        'placeholder'] = _("Invoice number")
        self.fields['note'].widget.attrs['placeholder'] = _('Order notes')
