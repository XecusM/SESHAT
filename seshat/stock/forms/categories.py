from django import forms
from django.utils.translation import gettext_lazy as _

from .. import models


class CategoryForm(forms.ModelForm):
    '''
    Form for item's category
    '''
    class Meta:
        model = models.Category
        fields = ['name', ]

    def __init__(self, *args, **kwargs):
        '''
        Method for initial values and functions
        '''
        super().__init__(*args, **kwargs)
        self.fields['name'].widget.attrs['placeholder'] = _('Category name')
