from django.core.exceptions import ValidationError
from django.db import models, transaction
from django.urls import reverse
from django.utils.translation import gettext_lazy as _

from x_django_app.models import XModel

from stock.models import ItemMove

# Create your models here.


class PurchaseOrder(models.Model, XModel):
    '''
    Store all purchase orders
    '''
    company = models.ForeignKey(
                        'vendor.VendorCompany',
                        verbose_name=_('Company'),
                        related_name='order_company',
                        on_delete=models.PROTECT,
                        blank=False,
                        null=False
    )
    invoice = models.CharField(
                        verbose_name=_('Invoice number'),
                        max_length=128,
                        unique=False,
                        blank=True,
                        null=True
    )
    invoice_date = models.DateField(
                        verbose_name=_('Invoice date'),
                        null=True,
                        blank=True
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
        verbose_name = _('Purchase order')
        verbose_name_plural = _('Purchase orders')
        ordering = ('-created_at', '-id')

    def clean(self):
        '''
        The invoice number and date go together
        '''
        if bool(self.invoice) != bool(self.invoice_date):
            raise ValidationError(
                _("Must complete invoice details (number and date)"),
                code='invoice_details')

    def get_absolute_url(self):
        return reverse('purchase:OrderDetails', kwargs={'pk': self.pk})

    @property
    def total_price(self):
        '''
        Calculate the total price of the order
        '''
        return sum((line.total_price for line in self.get_items()), 0)

    def get_items(self):
        '''
        Get all lines of the order
        '''
        return self.purchase_order.select_related(
                                    'item', 'item__item').order_by('id')

    def set_items(self, lines):
        '''
        Save the order lines. lines is a list of dicts with item, quantity,
        price and note. Existing lines are updated in place, extra lines
        deleted and new lines created, each with its stock move.
        Raises ValidationError when the stock can't allow it.
        '''
        with transaction.atomic():
            existing = list(self.get_items())
            for index, line in enumerate(lines):
                item = line['item']
                if index < len(existing):
                    order_line = existing[index]
                    move = order_line.item
                    move.item = item
                    move.location = item.location
                    move.quantity = line['quantity']
                    move.note = line.get('note') or None
                    move.save()
                else:
                    move = ItemMove.objects.create(
                                item=item,
                                location=item.location,
                                type=ItemMove.ADD,
                                related_to=ItemMove.PURCHASE,
                                quantity=line['quantity'],
                                note=line.get('note') or None)
                    order_line = PurchaseItem(order=self, item=move)
                order_line.price = line['price']
                order_line.note = line.get('note') or None
                order_line.save()
            for order_line in existing[len(lines):]:
                order_line.delete()

    def delete(self, *args, **kwargs):
        '''
        Delete the order with its lines and their stock moves
        '''
        with transaction.atomic():
            for line in self.get_items():
                line.delete()
            return super().delete(*args, **kwargs)

    def __str__(self):
        '''
        String representation for the record
        '''
        return f"{self.id}-{self.company.name}"


class PurchaseItem(models.Model):
    '''
    Store all orders' lines
    '''
    order = models.ForeignKey(
                        'PurchaseOrder',
                        verbose_name=_('Order'),
                        related_name='purchase_order',
                        on_delete=models.CASCADE,
                        blank=False,
                        null=False
    )
    item = models.OneToOneField(
                        ItemMove,
                        limit_choices_to={'type': ItemMove.ADD},
                        verbose_name=_('Item'),
                        related_name='purchase_item',
                        on_delete=models.PROTECT,
                        blank=False,
                        null=False
    )
    price = models.DecimalField(
                        verbose_name=_('Unit Price'),
                        max_digits=12,
                        decimal_places=2,
                        unique=False,
                        blank=False,
                        null=False
    )
    note = models.CharField(
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
        verbose_name = _('Purchase order line')
        verbose_name_plural = _('Purchase order lines')

    @property
    def quantity(self):
        '''
        The line quantity (from its stock move)
        '''
        return self.item.quantity

    @property
    def total_price(self):
        '''
        Calculate the total price for the line
        '''
        return self.price * self.item.quantity

    def delete(self, *args, **kwargs):
        '''
        Delete the line with its stock move
        '''
        with transaction.atomic():
            item_move = self.item
            result = super().delete(*args, **kwargs)
            item_move.delete()
            return result

    def __str__(self):
        '''
        String representation for the record
        '''
        return f"{self.order_id}-{self.item.item.code}"

