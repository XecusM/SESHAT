from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.db.models import Sum
from django.utils.translation import ugettext_lazy as _
from django.core.exceptions import ValidationError

from vendor import models as vendors_models
from stock import models as stock_models

# Create your models here.


class PurchaseOrder(models.Model):
    '''
    Store all purchase orders
    '''
    company = models.ForeignKey(
                        vendors_models.VendorCompany,
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
    edited_at = models.DateTimeField(
                        verbose_name=_('Edited at'),
                        null=True,
                        blank=True
    )
    edited_by = models.ForeignKey(
                        get_user_model(),
                        verbose_name=_('Edited by'),
                        related_name='vendor_order_user_edit',
                        on_delete=models.PROTECT,
                        blank=True,
                        null=True
    )
    created_at = models.DateTimeField(
                        verbose_name=_('Created at'),
                        auto_now_add=True,
                        blank=False
    )
    created_by = models.ForeignKey(
                        get_user_model(),
                        verbose_name=_('Created by'),
                        related_name='vendor_order_user_create',
                        on_delete=models.PROTECT,
                        blank=True,
                        null=True
    )

    @property
    def total_price(self):
        '''
        Calculate the total price of the order
        '''
        items = self.purchase_order.filter(order=self.id)
        total_price = 0
        for item in items:
            total_price += item.total_price

        return total_price

    def get_items(self):
        '''
        Get all items for the selected order
        '''
        return self.purchase_order.filter(order=self.id).order_by('id')

    def edited(self, user):
        '''
        Edit Company
        '''
        self.edited_at = timezone.now()
        self.edited_by = user
        self.save()

    def delete(self):
        '''
        Delete Item
        '''
        item_moves = (move.item for move in self.get_items())
        super().delete()
        for item_move in item_moves:
            item_move.delete()

    def save(self, *args, **kwargs):
        '''
        Save record method
        '''
        if self.invoice and self.invoice_date:
            super().save(*args, **kwargs)
        elif not self.invoice and not self.invoice_date:
            super().save(*args, **kwargs)
        else:
            raise ValidationError(
                _("Must complete invoice details"))

    def __str__(self):
        '''
        String representation for the record
        '''
        return f"{self.id}-{self.company.name}"


class PurchaseItems(models.Model):
    '''
    Store all ordes' items
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
                        stock_models.ItemMove,
                        limit_choices_to={'type': stock_models.ItemMove.ADD},
                        verbose_name=_('Item'),
                        related_name='purchase_item',
                        on_delete=models.PROTECT,
                        blank=False,
                        null=False
    )
    price = models.DecimalField(
                        verbose_name=_('Unit Price'),
                        max_digits=8,
                        decimal_places=2,
                        unique=False,
                        blank=False,
                        null=False
    )
    note = models.CharField(
                        verbose_name=_('Notes'),
                        max_length=128,
                        unique=False,
                        blank=True,
                        null=True
    )
    edited_at = models.DateTimeField(
                        verbose_name=_('Edited at'),
                        null=True,
                        blank=True
    )
    edited_by = models.ForeignKey(
                        get_user_model(),
                        verbose_name=_('Edited by'),
                        related_name='vendor_purchase_user_edit',
                        on_delete=models.PROTECT,
                        blank=True,
                        null=True
    )
    created_at = models.DateTimeField(
                        verbose_name=_('Created at'),
                        auto_now_add=True,
                        blank=False
    )
    created_by = models.ForeignKey(
                        get_user_model(),
                        verbose_name=_('Created by'),
                        related_name='vendor_purchase_user_create',
                        on_delete=models.PROTECT,
                        blank=True,
                        null=True
    )

    @property
    def total_price(self):
        '''
        Calculate the total price for the item
        '''
        return self.price * self.item.quantity

    def edited(self, user):
        '''
        Edit item
        '''
        self.edited_at = timezone.now()
        self.edited_by = user
        self.save()

    def delete(self):
        '''
        Delete Item
        '''
        item_move = self.item
        super().delete()
        item_move.delete()

    def __str__(self):
        '''
        String representation for the record
        '''
        return f"{self.id}-{self.company.name}"
