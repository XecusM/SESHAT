from django import forms
from PIL import Image
from django.utils.translation import ugettext_lazy as _

from . import models


class CategoryFrom(forms.ModelForm):
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
        # get the initial form class values
        super().__init__(*args, **kwargs)
        # initate is_active
        self.fields['name'].widget.attrs['placeholder'] = _('Category name')


class ItemForm(forms.ModelForm):
    '''
    Form for items
    '''
    #############################################################
    # Fields for image cropping
    x = forms.FloatField(widget=forms.HiddenInput(), required=False)
    y = forms.FloatField(widget=forms.HiddenInput(), required=False)
    width = forms.FloatField(widget=forms.HiddenInput(), required=False)
    height = forms.FloatField(widget=forms.HiddenInput(), required=False)
    #############################################################

    class Meta:
        model = models.Item
        fields = [
                    'code', 'desciption', 'barcode', 'stock_limit', 'price',
                    'location', 'category', 'is_active', 'photo'
        ]

    def __init__(self, *args, **kwargs):
        '''
        Method for initial values and functions
        '''
        # get the initial form class values
        super().__init__(*args, **kwargs)
        # initate is_active
        self.fields['code'].widget.attrs['placeholder'] = _('Item code')
        self.fields['desciption'].widget.attrs[
                                        'placeholder'] = _('Item desciption')
        self.fields['barcode'].widget.attrs['placeholder'] = _('item barcode')
        self.fields['price'].help_text = _("Enter itme's selling unit price")
        self.fields['price'].widget.attrs['placeholder'] = _('item price')
        self.fields['stock_limit'].widget.attrs['placeholder'] = _('Limit')
        self.fields['stock_limit'].help_text = _(
                            "Enter the warning stock limit to re-order item")
        self.fields['photo'].help_text = _(
                            "Item photo must be at least 500x500")

    def save(self, commit=True):
        '''
        save for with cropped image
        '''
        form = super().save(commit=True)
        # check if image sent
        if form.photo:
            try:
                # get cropping data
                x = self.cleaned_data.get('x')
                y = self.cleaned_data.get('y')
                w = self.cleaned_data.get('width')
                h = self.cleaned_data.get('height')

                # get the save image path
                image = Image.open(form.photo.path)
                cropped_image = image.crop((x, y, w + x, h + y))
                # check if image size more than 500kb
                if cropped_image.size[0] * cropped_image.size[1] < \
                        0.5 * 1024 * 1024:
                    raise forms.ValidationError(
                                    _('Image file too small ( < 500kb )'))
                else:
                    # resize the image after cropping
                    resized_image = cropped_image.resize(
                                                        (500, 500),
                                                        Image.ANTIALIAS)
                    resized_image.save(form.photo.path)
                    return form
            except Exception as error_type:
                print(error_type)
                form.save()
                return form
        else:
            form.save()
            return form


class AssemblyItemForm(forms.ModelForm):
    '''
    Form for assembled items
    '''
    class Meta:
        model = models.AssemblyItem
        fields = ['item', 'sub_item', 'quantity', ]


class LocationForm(forms.ModelForm):
    '''
    Form for locations
    '''
    class Meta:
        model = models.Location
        fields = ['name',  ]

    def __init__(self, *args, **kwargs):
        '''
        Method for initial values and functions
        '''
        # get the initial form class values
        super().__init__(*args, **kwargs)
        # initate is_active
        self.fields['name'].widget.attrs['placeholder'] = _('Location name')


class SubLocationForm(forms.ModelForm):
    '''
    Form for sublocations
    '''
    class Meta:
        model = models.SubLocation
        fields = ['location', 'name', ]

    def __init__(self, *args, **kwargs):
        '''
        Method for initial values and functions
        '''
        # get the initial form class values
        super().__init__(*args, **kwargs)
        # initate is_active
        self.fields['location'].help_text = _("Select location")
        self.fields['name'].widget.attrs['placeholder'] = _('Location name')
        self.fields['name'].help_text = _("Sub-location name")


class ItemMoveForm(forms.ModelForm):
    '''
    Form for items' movements
    '''
    # error messages for email and password matches
    error_messages = {
        'quantity_error': _(
                    "Quantity can't be negative for the selected location"),
        'item_error': _("Must choose valid item"),
        'type_error': _("Must choose valid type"),
        'location_error': _("Must choose valid location"),
    }
    class Meta:
        model = models.ItemMove
        fields = ['item', 'type', 'location', 'quantity', 'note', ]
        labels = {"note": _('Notes*')}

    def clean_quantity(self):
        '''
        Method to clean quantity
        '''
        cleaned_data = self.cleaned_data
        item = cleaned_data.get('item')
        location = cleaned_data.get('location')
        type = cleaned_data.get('type')
        if not item:
            raise forms.ValidationError(
            self.error_messages['item_error'],
            code='item_error')
        if not location:
            raise forms.ValidationError(
            self.error_messages['location_error'],
            code='location_error')
        if not type:
            raise forms.ValidationError(
            self.error_messages['type_error'],
            code='type_error')
        quantity = int(self.cleaned_data.get('quantity'))
        if item.get_quantity(location.id) < quantity and \
                type == models.ItemMove.REMOVE:
            raise forms.ValidationError(
                self.error_messages['quantity_error'],
                code='quantity_error')
        else:
            return quantity

    def __init__(self, *args, **kwargs):
        '''
        Method for initial values and functions
        '''
        # get the initial form class values
        super().__init__(*args, **kwargs)
        # initate is_active
        self.fields['note'].widget.attrs['required'] = 'required'
        self.fields['note'].widget.attrs['placeholder'
                                        ] = _('Add notes for this custom move')
        self.fields['quantity'].widget.attrs['min'] = 0
        self.fields['quantity'].widget.attrs['placeholder'
                                                ] = _('Add desired quantity')
        self.fields['location'].help_text = _("Select location")
        self.fields['type'].help_text = _("Select movement type")


class ItemTransferForm(forms.ModelForm):
    '''
    Form for item transfer from location to another
    '''
    quantity = forms.IntegerField()
    class Meta:
        model = models.ItemTransfer
        fields = ['item', 'old_location', 'new_location', 'quantity', ]

    def __init__(self, *args, **kwargs):
        '''
        Method for initial values and functions
        '''
        # get the initial form class values
        super().__init__(*args, **kwargs)
        # initate is_active
        self.fields['quantity'].widget.attrs['min'] = 0
        self.fields['quantity'].widget.attrs[
                                'placeholder'] = _('Add desired quantity')
        self.fields['old_location'].help_text = _("Select old location")
        self.fields['new_location'].help_text = _("Select new location")
