from django import forms
from django.forms import inlineformset_factory, BaseInlineFormSet
from django.utils.translation import gettext_lazy as _

from seshat.images import crop_and_resize

from .. import models


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
                    'code', 'description', 'barcode', 'category',
                    'location', 'price', 'stock_limit', 'is_assembly',
                    'is_active', 'note', 'photo',
                    'x', 'y', 'width', 'height',
        ]
        widgets = {
            'note': forms.Textarea(attrs={'rows': 3}),
            'photo': forms.FileInput(attrs={'accept': 'image/*'}),
        }

    def __init__(self, *args, **kwargs):
        '''
        Method for initial values and functions
        '''
        super().__init__(*args, **kwargs)
        self.fields['code'].widget.attrs['placeholder'] = _('Item code')
        self.fields['description'].widget.attrs[
                                    'placeholder'] = _('Item description')
        self.fields['barcode'].widget.attrs['placeholder'] = _('Item barcode')
        self.fields['price'].help_text = _("Enter item's selling unit price")
        self.fields['price'].widget.attrs['placeholder'] = _('Item price')
        self.fields['stock_limit'].widget.attrs['placeholder'] = _('Limit')
        self.fields['stock_limit'].help_text = _(
                            "Warning stock limit to re-order the item")
        self.fields['is_assembly'].help_text = _(
                            "An assembled item is built from other items")
        self.fields['photo'].help_text = _(
                            "Item photo is recommended to be at least 500x500")
        self.fields['location'].queryset = models.SubLocation.objects.select_related(
                                                                'location')
        if self.instance.pk:
            # an item can't switch between normal and assembled
            self.fields['is_assembly'].disabled = True

    def save(self, commit=True):
        '''
        Save the item with its photo cropped and resized to 500x500
        '''
        instance = super().save(commit=commit)
        if commit and 'photo' in self.changed_data and instance.photo:
            crop_and_resize(
                        instance.photo.path,
                        self.cleaned_data.get('x'),
                        self.cleaned_data.get('y'),
                        self.cleaned_data.get('width'),
                        self.cleaned_data.get('height'),
                        size=500)
        return instance


class AssemblyItemForm(forms.ModelForm):
    '''
    Form for one component of an assembled item
    '''
    class Meta:
        model = models.AssemblyItem
        fields = ['sub_item', 'quantity', ]

    def __init__(self, *args, **kwargs):
        '''
        Only active, not assembled, items can be components
        '''
        super().__init__(*args, **kwargs)
        self.fields['sub_item'].queryset = models.Item.objects.filter(
                                is_assembly=False, is_active=True).order_by('code')
        self.fields['quantity'].widget.attrs['min'] = 1


class BaseAssemblyItemFormSet(BaseInlineFormSet):
    '''
    Validate the components of an assembled item
    '''

    def clean(self):
        '''
        Components must be unique, and an assembled item needs at least one
        '''
        super().clean()
        if any(self.errors):
            return
        sub_items = []
        for form in self.forms:
            if not form.cleaned_data or form.cleaned_data.get('DELETE'):
                continue
            sub_item = form.cleaned_data.get('sub_item')
            if sub_item in sub_items:
                raise forms.ValidationError(
                            _("Can't choose the same item twice."),
                            code='duplicate_item')
            if self.instance.pk and sub_item == self.instance:
                raise forms.ValidationError(
                            _("An item can't be a component of itself."),
                            code='self_component')
            sub_items.append(sub_item)
        if not sub_items:
            raise forms.ValidationError(
                        _("An assembled item needs at least one component."),
                        code='no_components')


AssemblyItemFormSet = inlineformset_factory(
                                models.Item,
                                models.AssemblyItem,
                                form=AssemblyItemForm,
                                formset=BaseAssemblyItemFormSet,
                                fk_name='item',
                                extra=1,
                                can_delete=True)
