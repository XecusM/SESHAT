from django import forms
from django.utils.translation import gettext_lazy as _

from .. import models


class LocationForm(forms.ModelForm):
    '''
    Form for locations
    '''
    class Meta:
        model = models.Location
        fields = ['name', ]

    def __init__(self, *args, **kwargs):
        '''
        Method for initial values and functions
        '''
        super().__init__(*args, **kwargs)
        self.fields['name'].widget.attrs['placeholder'] = _('Location name')


class SubLocationForm(forms.ModelForm):
    '''
    Form for sub-locations
    '''
    class Meta:
        model = models.SubLocation
        fields = ['location', 'name', ]

    def __init__(self, *args, **kwargs):
        '''
        Method for initial values and functions
        '''
        super().__init__(*args, **kwargs)
        self.fields['location'].help_text = _("Select location")
        self.fields['name'].widget.attrs['placeholder'] = _(
                                                        'Sub-location name')
