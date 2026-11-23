from django.core.validators import MinValueValidator
from django.db import models
from django.db.models import Q, Sum
from django.dispatch import receiver
from django.utils.translation import gettext_lazy as _

from x_django_app.models import XModel

import uuid
import os

# Help Functions


def get_image_path(instance, filename):
    '''
    Uploading image function
    '''
    ext = filename.split('.')[-1]
    filename = f'{uuid.uuid4()}.{ext}'

    return os.path.join('items/', filename)


def moves_balance(moves):
    '''
    Return the added quantity minus the removed quantity of the moves
    '''
    from .moves import ItemMove
    totals = moves.aggregate(
                added=Sum('quantity', filter=Q(type=ItemMove.ADD)),
                removed=Sum('quantity', filter=Q(type=ItemMove.REMOVE)))
    return int((totals['added'] or 0) - (totals['removed'] or 0))


class Item(models.Model, XModel):
    '''
    Model for the stock items
    '''
    code = models.CharField(
                            verbose_name=_('Code'),
                            max_length=32,
                            unique=True,
                            blank=False,
                            null=False
    )
    description = models.CharField(
                            verbose_name=_('Description'),
                            max_length=128,
                            unique=False,
                            blank=True,
                            null=True
    )
    barcode = models.CharField(
                            verbose_name=_('Barcode'),
                            max_length=128,
                            unique=True,
                            blank=True,
                            null=True
    )
    stock_limit = models.PositiveIntegerField(
                            verbose_name=_('Stock Limit'),
                            unique=False,
                            blank=True,
                            null=True
    )
    is_assembly = models.BooleanField(
                            verbose_name=_('Assembled Item'),
                            default=False
    )
    category = models.ForeignKey(
                            'Category',
                            verbose_name=_('Category'),
                            related_name='item_category',
                            on_delete=models.PROTECT,
                            blank=False,
                            null=False
    )
    location = models.ForeignKey(
                            'SubLocation',
                            verbose_name=_('Default Location'),
                            related_name='item_location',
                            on_delete=models.PROTECT,
                            blank=False,
                            null=False
    )
    price = models.DecimalField(
                            verbose_name=_('Unit Price'),
                            max_digits=12,
                            decimal_places=2,
                            validators=[MinValueValidator(0)],
                            unique=False,
                            blank=False,
                            null=False
    )
    photo = models.ImageField(
                            verbose_name=_('Item Picture'),
                            upload_to=get_image_path,
                            null=True,
                            blank=True
    )
    is_active = models.BooleanField(
                            verbose_name=_('Enabled'),
                            default=True
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
        verbose_name = _('Item')
        verbose_name_plural = _('Items')
        ordering = ('code', )

    def clean(self):
        '''
        Change cleaned data before save to database
        '''
        self.code = str(self.code).strip().upper()
        if not self.barcode:
            self.barcode = None

    @property
    def quantity(self):
        '''
        return the item quantity from its movements. An assembled item's
        quantity is how many units can be built from its components.
        '''
        if self.is_assembly:
            quantities = [
                    component.sub_item.quantity // component.quantity
                    for component in self.get_assembly_items()
                    if component.quantity > 0]
            return max(min(quantities), 0) if quantities else 0
        return moves_balance(self.item_move_item.all())

    @property
    def is_low_stock(self):
        '''
        Whether the quantity reached the re-order limit
        '''
        return self.stock_limit is not None and \
            self.quantity <= self.stock_limit

    @property
    def stock_value(self):
        '''
        The value of the item's quantity at its unit price
        '''
        return self.quantity * self.price

    def get_item_moves(self):
        '''
        Get all item moves
        '''
        return self.item_move_item.all().order_by('-created_at', '-id')

    def get_assembly_items(self):
        '''
        Get the components of an assembled item
        '''
        return self.assembly_item.select_related(
                                        'sub_item').order_by('id')

    def get_quantity(self, location):
        '''
        Get the available quantity in a sub-location (object or id)
        '''
        if self.is_assembly:
            return self.quantity
        return moves_balance(self.item_move_item.filter(location=location))

    def get_locations(self):
        '''
        Get the quantities by sub-location
        '''
        if self.is_assembly:
            return []
        from .locations import SubLocation
        sub_locations = SubLocation.objects.filter(
                        item_move_location__item=self).distinct().select_related(
                        'location').order_by('location__name', 'name')
        return [{
                    'id': sub_location.id,
                    'name': str(sub_location),
                    'quantity': self.get_quantity(sub_location),
                } for sub_location in sub_locations]

    def can_be_deleted(self):
        '''
        An item with moves or used in an assembly can't be deleted
        '''
        return not (self.item_move_item.exists()
                    or self.assembly_sub_item.exists())

    def __str__(self):
        '''
        String representation for the record
        '''
        return self.code


class AssemblyItem(models.Model):
    '''
    link the component items to an assembled item
    '''
    item = models.ForeignKey(
                            'Item',
                            verbose_name=_('Assembled Item'),
                            limit_choices_to={'is_assembly': True},
                            related_name='assembly_item',
                            on_delete=models.CASCADE,
                            blank=False,
                            null=False
    )
    sub_item = models.ForeignKey(
                            'Item',
                            verbose_name=_('Component'),
                            limit_choices_to={'is_assembly': False},
                            related_name='assembly_sub_item',
                            on_delete=models.PROTECT,
                            blank=False,
                            null=False
    )
    quantity = models.PositiveIntegerField(
                            verbose_name=_('Quantity'),
                            validators=[MinValueValidator(1)],
                            unique=False,
                            blank=False,
                            null=False
    )
    created_at = models.DateTimeField(
                            verbose_name=_('Created at'),
                            auto_now_add=True,
                            blank=False
    )

    class Meta:
        verbose_name = _('Assembly component')
        verbose_name_plural = _('Assembly components')
        constraints = [
            models.UniqueConstraint(
                        fields=['item', 'sub_item'],
                        name='unique_assembly_component'),
        ]

    @property
    def sub_item_quantity(self):
        '''
        return the component's available quantity
        '''
        return self.sub_item.quantity

    def __str__(self):
        '''
        String representation for the record
        '''
        return f"{self.item.code}/{self.sub_item.code}"


# Signals
@receiver(models.signals.post_delete, sender=Item)
def auto_delete_file_on_delete(sender, instance, **kwargs):
    '''
    Deletes file from filesystem
    when corresponding `Item` object is deleted.
    '''
    if instance.photo and os.path.isfile(instance.photo.path):
        os.remove(instance.photo.path)


@receiver(models.signals.pre_save, sender=Item)
def auto_delete_file_on_change(sender, instance, raw=False, **kwargs):
    '''
    Deletes old file from filesystem
    when corresponding `Item` object is updated
    with new file.
    '''
    if raw or not instance.pk:
        return
    try:
        old_photo = Item.objects.get(pk=instance.pk).photo
    except Item.DoesNotExist:
        return
    new_photo = instance.photo
    if not old_photo == new_photo and old_photo and \
            os.path.isfile(old_photo.path):
        os.remove(old_photo.path)
