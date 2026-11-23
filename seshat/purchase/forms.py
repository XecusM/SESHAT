from django import forms
from django.forms import formset_factory, BaseFormSet
from django.utils.translation import gettext_lazy as _

from stock.models import Item

from . import models

# Order lines settings: the unit price must be entered for purchases, and
# only normal (not assembled) active items can be purchased
PRICE_REQUIRED = True


def ITEMS_QUERYSET():
    return Item.objects.filter(
                        is_active=True, is_assembly=False).order_by('code')


class OrderForm(forms.ModelForm):
    '''
    Form for order
    '''
    class Meta:
        model = models.PurchaseOrder
        fields = ['company', 'invoice', 'invoice_date', 'note', ]

        widgets = {
            'invoice_date': forms.DateInput(
                                    attrs={'type': 'date'},
                                    format='%Y-%m-%d'),
            'note': forms.Textarea(attrs={'rows': 2}),
        }

    def __init__(self, *args, **kwargs):
        '''
        Method for initial values and functions
        '''
        super().__init__(*args, **kwargs)
        self.fields['company'].help_text = _("Select company")
        self.fields['invoice'].widget.attrs['placeholder'] = _(
                                                        "Invoice number")
        self.fields['note'].widget.attrs['placeholder'] = _('Order notes')


class OrderLineForm(forms.Form):
    '''
    Form for one line of the order
    '''
    item = forms.ModelChoiceField(
                            label=_('Item'),
                            queryset=Item.objects.none())
    quantity = forms.IntegerField(label=_('Quantity'), min_value=1)
    price = forms.DecimalField(
                            label=_('Unit Price'),
                            min_value=0,
                            max_digits=12,
                            decimal_places=2,
                            required=PRICE_REQUIRED)
    note = forms.CharField(label=_('Notes'), max_length=255, required=False)

    def __init__(self, *args, **kwargs):
        '''
        Method for initial values and functions
        '''
        super().__init__(*args, **kwargs)
        self.fields['item'].queryset = ITEMS_QUERYSET()
        self.fields['quantity'].widget.attrs['min'] = 1
        self.fields['price'].widget.attrs['step'] = '0.01'


class BaseOrderLineFormSet(BaseFormSet):
    '''
    Validate the order lines
    '''

    def clean(self):
        '''
        An item can be added only once
        '''
        super().clean()
        if any(self.errors):
            return
        items = []
        for form in self.forms:
            if not form.cleaned_data or form.cleaned_data.get('DELETE'):
                continue
            item = form.cleaned_data.get('item')
            if item in items:
                raise forms.ValidationError(
                            _("Can't choose the same item twice."),
                            code='duplicate_item')
            items.append(item)
        if not items:
            raise forms.ValidationError(
                        _("The order needs at least one item."),
                        code='no_items')

    def get_lines(self):
        '''
        Return the valid lines as a list of dicts
        '''
        lines = []
        for form in self.forms:
            if not form.cleaned_data or form.cleaned_data.get('DELETE'):
                continue
            line = dict(form.cleaned_data)
            line.pop('DELETE', None)
            if line.get('price') is None:
                line['price'] = line['item'].price
            lines.append(line)
        return lines


OrderLineFormSet = formset_factory(
                                OrderLineForm,
                                formset=BaseOrderLineFormSet,
                                extra=0,
                                can_delete=True)
