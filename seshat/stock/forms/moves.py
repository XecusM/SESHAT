from django import forms
from django.utils.translation import gettext_lazy as _

from .. import models


class ItemMoveForm(forms.ModelForm):
    '''
    Form for a custom item movement (add or remove)
    '''
    class Meta:
        model = models.ItemMove
        fields = ['type', 'location', 'quantity', 'note', ]
        widgets = {
            'note': forms.Textarea(attrs={'rows': 3}),
        }

    def __init__(self, *args, **kwargs):
        '''
        Method for initial values and functions
        '''
        self.item = kwargs.pop('item')
        super().__init__(*args, **kwargs)
        self.instance.item = self.item
        self.instance.related_to = models.ItemMove.CUSTOM
        self.fields['note'].required = True
        self.fields['note'].widget.attrs['placeholder'] = _(
                                        'Add notes for this custom move')
        self.fields['quantity'].widget.attrs['min'] = 1
        self.fields['quantity'].widget.attrs['placeholder'] = _(
                                        'Add desired quantity')
        self.fields['location'].help_text = _("Select location")
        self.fields['location'].initial = self.item.location_id
        self.fields['type'].help_text = _("Select movement type")

    def clean(self):
        '''
        Check the available quantity
        '''
        cleaned_data = super().clean()
        if self.errors:
            return cleaned_data
        move = self.instance
        move.type = cleaned_data.get('type')
        move.location = cleaned_data.get('location')
        move.quantity = cleaned_data.get('quantity')
        try:
            move.validate_stock()
        except forms.ValidationError as error:
            self.add_error('quantity', error)
        return cleaned_data


class ItemTransferForm(forms.Form):
    '''
    Form for an item transfer from a sub-location to another
    '''
    old_location = forms.ModelChoiceField(
                            label=_('From Location'),
                            queryset=models.SubLocation.objects.none())
    new_location = forms.ModelChoiceField(
                            label=_('To Location'),
                            queryset=models.SubLocation.objects.none())
    quantity = forms.IntegerField(label=_('Quantity'), min_value=1)
    note = forms.CharField(
                            label=_('Notes'),
                            required=False,
                            widget=forms.Textarea(attrs={'rows': 2}))

    def __init__(self, *args, **kwargs):
        '''
        Method for initial values and functions
        '''
        self.item = kwargs.pop('item')
        super().__init__(*args, **kwargs)
        sub_locations = models.SubLocation.objects.select_related('location')
        self.fields['old_location'].queryset = sub_locations.filter(
                        item_move_location__item=self.item).distinct()
        self.fields['new_location'].queryset = sub_locations
        self.fields['quantity'].widget.attrs['placeholder'] = _(
                                                    'Add desired quantity')
        self.fields['old_location'].help_text = _(
                                    "Select the location to move from")
        self.fields['new_location'].help_text = _(
                                    "Select the location to move to")

    def clean(self):
        '''
        Check the locations and the available quantity
        '''
        cleaned_data = super().clean()
        old_location = cleaned_data.get('old_location')
        new_location = cleaned_data.get('new_location')
        quantity = cleaned_data.get('quantity')
        if old_location and new_location and old_location == new_location:
            self.add_error(
                        'new_location',
                        _("The two locations must be different"))
        if old_location and quantity and \
                self.item.get_quantity(old_location) < quantity:
            self.add_error(
                        'quantity',
                        _("Only %(available)s available in the selected "
                          "location") % {
                            'available': self.item.get_quantity(old_location)})
        return cleaned_data

    def save(self):
        '''
        Create the transfer and its two moves
        '''
        return models.ItemTransfer.transfer(
                        self.item,
                        self.cleaned_data['old_location'],
                        self.cleaned_data['new_location'],
                        self.cleaned_data['quantity'],
                        self.cleaned_data.get('note') or None)
