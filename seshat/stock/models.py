from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _
from django.dispatch import receiver
from django.db.models import Sum
from django.db.models import Q
from django.http import Http404
from django.core.validators import MinValueValidator
from django.core.exceptions import ValidationError

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

# Create your models here.


class Category(models.Model):
    '''
    Model for items categories
    '''
    name = models.CharField(
                        verbose_name=_('Category name'),
                        max_length=128,
                        unique=True,
                        blank=False,
                        null=False
    )
    edited_at = models.DateTimeField(
                        verbose_name=_('Edited at'),
                        null=True,
                        blank=True
    )
    edited_by = models.ForeignKey(
                        get_user_model(),
                        verbose_name=_('Edited by'),
                        related_name='category_item_user_edit',
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
                        related_name='category_item_user_create',
                        on_delete=models.PROTECT,
                        blank=True,
                        null=True
    )

    def clean(self):
        '''
        Change cleaed data before save to datase
        '''
        self.name = self.name.capitalize()

    def get_items(self):
        '''
        Get all items for selected category
        '''
        return self.item_category.filter(category=self.id)

    def edited(self, user):
        '''
        Edit Category
        '''
        self.edited_at = timezone.now()
        self.edited_by = user
        self.save()

    def __str__(self):
        '''
        String representation for the record
        '''
        return self.name


class Item(models.Model):
    '''
    Model for the items
    '''
    code = models.CharField(
                            verbose_name=_('Code'),
                            max_length=8,
                            unique=True,
                            blank=False,
                            null=False
    )
    desciption = models.CharField(
                            verbose_name=_('Desciption'),
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
    stock_limit = models.IntegerField(
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
                            max_digits=8,
                            decimal_places=2,
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
    edited_at = models.DateTimeField(
                            verbose_name=_('Edited at'),
                            null=True,
                            blank=True
    )
    edited_by = models.ForeignKey(
                            get_user_model(),
                            verbose_name=_('Edited by'),
                            related_name='item_user_edit',
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
                            related_name='item_user_create',
                            on_delete=models.PROTECT,
                            blank=True,
                            null=True
    )

    def clean(self):
        '''
        Change cleaed data before save to datase
        '''
        # let code be upper case only
        self.code = self.code.upper()

    @property
    def quantity(self):
        '''
        return item quantity from its movements
        '''
        if self.is_assembly:
            assembly_item = self.assembly_item.filter(item=self.id)
            quantity = None
            if assembly_item:
                for item in assembly_item:
                    if quantity is None:
                        quantity = int(int(item.sub_item.quantity) \
                                        / item.quantity)
                    else:
                        quantity = min(
                                    quantity,
                                    int(int(item.sub_item.quantity) \
                                        / item.quantity))
                return int(quantity)
            else:
                raise ValidationError(
                                _("Can't find items for assemblied item"))
        else:
            # sum all add movements
            sum_add = self.item_move_item.filter(
                                    item=self.id,
                                    type='A').aggregate(Sum('quantity'))
            if sum_add['quantity__sum'] is None:
                sum_add['quantity__sum'] = 0

            # sum all remove movements
            sum_remove = self.item_move_item.filter(
                                    item=self.id,
                                    type='R').aggregate(Sum('quantity'))
            if sum_remove['quantity__sum'] is None:
                sum_remove['quantity__sum'] = 0

            # calculate the deffreance between the add and remove sums
            sum_all = sum_add['quantity__sum'] - sum_remove['quantity__sum']

            return int(sum_all)

    def get_item_moves(self):
        '''
        Get all item moves
        '''
        return self.item_move_item.filter(
                                        item=self).order_by('-created_at')

    def get_assembly_items(self):
        '''
        Get all items for the selected assemblied item
        '''
        if self.is_assembly:
            return self.assembly_item.filter(item=self.id).order_by('id')
        else:
            raise ValidationError(_('This is not assembly item'))

    def get_quantity(self, location):
        '''
        Get avalible quantity for sublocation
        '''
        if self.is_assembly:
            return int(self.quantity)
        else:
            # sum all add movements
            sum_add = self.item_move_item.filter(
            item=self.id,
            location=location,
            type='A').aggregate(Sum('quantity'))
            if sum_add['quantity__sum'] is None:
                sum_add['quantity__sum'] = 0

            # sum all remove movements
            sum_remove = self.item_move_item.filter(
            item=self.id,
            location=location,
            type='R').aggregate(Sum('quantity'))
            if sum_remove['quantity__sum'] is None:
                sum_remove['quantity__sum'] = 0

            # calculate the deffreance between the add and remove sums
            sum_all = sum_add['quantity__sum'] - sum_remove['quantity__sum']
            return int(sum_all)

    def get_locations(self):
        '''
        Get quantities by location
        '''
        if not self.is_assembly:
            all_locations = [{
                        'name': f"{move.location.location.name} / {move.location.name}",
                        'id': move.location.id
                    } for move in self.item_move_item.filter(item=self.id)]
            # Remove deplucation
            locations = [d for i, d in enumerate(
                            all_locations) if d not in all_locations[i + 1:]]
            for i, location in enumerate(locations):
                # sum all add movements
                sum_add = self.item_move_item.filter(
                                                    item=self.id,
                                                    type='A',
                                                    location=location['id']
                                                ).aggregate(Sum('quantity'))
                if sum_add['quantity__sum'] is None:
                    sum_add['quantity__sum'] = 0
                # sum all remove movements
                sum_remove = self.item_move_item.filter(
                                                    item=self.id,
                                                    type='R',
                                                    location=location['id']
                                                ).aggregate(Sum('quantity'))
                if sum_remove['quantity__sum'] is None:
                    sum_remove['quantity__sum'] = 0

                # calculate the deffreance between the add and remove sums
                sum_all = sum_add[
                            'quantity__sum'] - sum_remove['quantity__sum']
                locations[i]['quantity'] = sum_all
            return locations

    def edited(self, user):
        '''
        Edit item
        '''
        self.edited_at = timezone.now()
        self.edited_by = user
        self.save()

    def __str__(self):
        '''
        String representation for the record
        '''
        return self.code


class AssemblyItem(models.Model):
    '''
    link all items to assemblied item
    '''
    item = models.ForeignKey(
                            'Item',
                            verbose_name=_('Item'),
                            limit_choices_to={'is_assembly': True},
                            related_name='assembly_item',
                            on_delete=models.CASCADE,
                            blank=False,
                            null=False
    )
    sub_item = models.ForeignKey(
                            'Item',
                            verbose_name=_('Item'),
                            related_name='assembly_sub_item',
                            on_delete=models.PROTECT,
                            blank=False,
                            null=False
    )
    quantity = models.IntegerField(
                            verbose_name=_('Quantity'),
                            unique=False,
                            blank=False,
                            null=False
    )
    created_at = models.DateTimeField(
                            verbose_name=_('Created at'),
                            auto_now_add=True,
                            blank=False
    )

    @property
    def sub_item_quantity(self):
        '''
        return asembled item quantity from its sub-items
        '''
        return self.sub_item.quantity

    def __str__(self):
        '''
        String representation for the record
        '''
        return f"{self.item.code}/{self.sub_item.code}"


class Location(models.Model):
    '''
    Model for item locations to store
    '''
    name = models.CharField(
                            verbose_name=_('Location name'),
                            max_length=128,
                            unique=True,
                            blank=False,
                            null=False
    )
    edited_at = models.DateTimeField(
                            verbose_name=_('Edited at'),
                            null=True,
                            blank=True
    )
    edited_by = models.ForeignKey(
                            get_user_model(),
                            verbose_name=_('Edited by'),
                            related_name='location_user_edit',
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
                            related_name='location_user_create',
                            on_delete=models.PROTECT,
                            blank=True,
                            null=True
    )

    def clean(self):
        '''
        Change cleaed data before save to datase
        '''
        self.name = self.name.upper()

    def get_sub_locations(self):
        '''
        Get all sub-locations for selected location
        '''
        return self.sub_location.filter(location=self.id)

    def edited(self, user):
        '''
        Edit location
        '''
        self.edited_at = timezone.now()
        self.edited_by = user
        self.save()

    def __str__(self):
        '''
        String representation for the record
        '''
        return self.name


class SubLocation(models.Model):
    '''
    Model for item sub-locations to store
    '''
    location = models.ForeignKey(
                            'Location',
                            verbose_name=_('Location'),
                            related_name='sub_location',
                            on_delete=models.PROTECT,
                            blank=False,
                            null=False
    )
    name = models.CharField(
                            verbose_name=_('Sub-location name'),
                            max_length=128,
                            unique=True,
                            blank=False,
                            null=False
    )
    edited_at = models.DateTimeField(
                            verbose_name=_('Edited at'),
                            null=True,
                            blank=True
    )
    edited_by = models.ForeignKey(
                            get_user_model(),
                            verbose_name=_('Edited by'),
                            related_name='sublocation_user_edit',
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
                            related_name='sublocation_user_create',
                            on_delete=models.PROTECT,
                            blank=True,
                            null=True
    )

    def clean(self):
        '''
        Change cleaed data before save to datase
        '''
        self.name = self.name.upper()

    def get_items(self):
        '''
        return all items in this sub-location
        '''
        item_moves = self.item_move_location.filter(location=self.id)

        return Item.objects.filter(item_move_item__in=item_moves)

    def edited(self, user):
        '''
        Edit sub-location
        '''
        self.edited_at = timezone.now()
        self.edited_by = user
        self.save()

    def __str__(self):
        '''
        String representation for the record
        '''
        return f"{self.location.name} / {self.name}"


class ItemMove(models.Model):
    '''
    Model for item movements done on the items
    '''
    #########################################
    # Choices
    ADD = 'A'
    REMOVE = 'R'
    type_choices = [
                    (ADD, _('Add')),
                    (REMOVE, _('Remove'))
    ]

    PURCHASE = 'P'
    SELL = 'S'
    ASSEMBLY = 'A'
    CUSTOM = 'U'
    TRANSFER = 'T'
    related_choices = [
                    (PURCHASE, _('Purchase')),
                    (SELL, _('Sell')),
                    (ASSEMBLY, _('Assembly')),
                    (CUSTOM, _('Custom')),
                    (TRANSFER, _('Transfer'))
    ]
    #########################################

    item = models.ForeignKey(
                            'Item',
                            verbose_name=_('Item'),
                            related_name='item_move_item',
                            on_delete=models.PROTECT,
                            blank=False,
                            null=False
    )
    location = models.ForeignKey(
                            'SubLocation',
                            verbose_name=_('Location'),
                            related_name='item_move_location',
                            on_delete=models.PROTECT,
                            blank=False,
                            null=False
    )
    type = models.CharField(
                            verbose_name=_('Movement type'),
                            max_length=1,
                            choices=type_choices,
                            blank=False,
                            null=False
    )
    quantity = models.IntegerField(
                            verbose_name=_('Quantity'),
                            validators=[MinValueValidator(1)],
                            unique=False,
                            blank=False,
                            null=False
    )
    related_to = models.CharField(
                            verbose_name=_('Related to'),
                            max_length=1,
                            choices=related_choices,
                            default=CUSTOM,
                            blank=False,
                            null=False
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
                            related_name='item_move_user_edit',
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
                            related_name='item_move_user_create',
                            on_delete=models.PROTECT,
                            blank=True,
                            null=True
    )

    def edited(self, user):
        '''
        Edit movement
        '''
        self.edited_at = timezone.now()
        self.edited_by = user
        self.save()

    def delete(self):
        '''
        Delete Item
        '''
        if self.item.is_assembly:
            moves_values = self.assembly_move_assembly_move.get(
                            id=self).item_moves.values_list('id', flat=True)
            item_moves = ItemMove.objects.filter(id__in=moves_values)
            for item_move in item_moves:
                item_move.delete()
        super().delete()

    def save(self, *args, **kwargs):
        '''
        Save record method
        '''
        if self.item.get_quantity(self.location.id) < int(self.quantity) and \
                self.type == ItemMove.REMOVE and not self.item.is_assembly:
            raise ValidationError(
                    _("Quantity can't be negative for the selected location"))
        else:
            super().save(*args, **kwargs)
            if self.item.is_assembly:
                if AssemblyMove.objects.filter(
                                            assembly_move=self).exists():
                    moves_values = self.assembly_move_assembly_move.get(
                                assembly_move=self).item_moves.values_list(
                                                                'id', flat=True)
                    item_moves = ItemMove.objects.filter(id__in=moves_values)
                    for item_move in item_moves:
                        item_move.quantity = self.quantity * (
                            sub_item.quantity for sub_item in self.item.get_assembly_items() if sub_item == self.item)
                        item_move.save()
                else:
                    sub_item_list = list()
                    for sub_item in self.item.get_assembly_items():
                        sub_item_move = ItemMove.objects.create(
                                item=sub_item.sub_item,
                                location=sub_item.sub_item.location,
                                type=self.type,
                                related_to=ItemMove.ASSEMBLY,
                                quantity=self.quantity * sub_item.quantity)
                        sub_item_list.append(sub_item_move)
                    assembly_move = AssemblyMove.objects.create(
                                        assembly_move=self)
                    for sub_item_add in sub_item_list:
                        assembly_move.item_moves.add(sub_item_add)
                        assembly_move.save()

    def __str__(self):
        '''
        String representation for the record
        '''
        return f"{self.type}-{self.id}"


class AssemblyMove(models.Model):
    '''
    Model for assemblied items retlated movements
    '''
    assembly_move = models.OneToOneField(
                            'ItemMove',
                            verbose_name=_('Item'),
                            limit_choices_to=~Q(related_to=ItemMove.ASSEMBLY),
                            related_name='assembly_move_assembly_move',
                            on_delete=models.CASCADE,
                            blank=False,
                            null=False
    )
    item_moves = models.ManyToManyField(
                            'ItemMove',
                            verbose_name=_("Items' moves"),
                            limit_choices_to={
                                        'related_to': ItemMove.ASSEMBLY},
                            related_name='assembly_move_item_move',
                            blank=True,
    )
    edited_at = models.DateTimeField(
                            verbose_name=_('Edited at'),
                            null=True,
                            blank=True
    )
    created_at = models.DateTimeField(
                            verbose_name=_('Created at'),
                            auto_now_add=True,
                            blank=False
    )

    def edited(self):
        '''
        Edit assembly movement
        '''
        self.edited_at = timezone.now()
        self.save()

    def delete(self):
        '''
        Delete Item
        '''
        moves_values = self.item_moves.values_list('id', flat=True)
        item_moves = ItemMove.objects.filter(id__in=moves_values)
        super().delete()
        for item_move in item_moves:
            item_move.delete()

    def __str__(self):
        '''
        String representation for the record
        '''
        return f"{self.assembly_move.item.code}-{self.id}"


class ItemTransfer(models.Model):
    '''
    Model for transfer item from location to another
    '''
    item = models.ForeignKey(
                            'Item',
                            verbose_name=_('Item'),
                            related_name='item_transfer_item',
                            on_delete=models.PROTECT,
                            blank=False,
                            null=False
    )
    old_location = models.ForeignKey(
                            'SubLocation',
                            verbose_name=_('Old Location'),
                            related_name='item_transfer_old_location',
                            on_delete=models.PROTECT,
                            blank=False,
                            null=False
    )
    new_location = models.ForeignKey(
                            'SubLocation',
                            verbose_name=_('New Location'),
                            related_name='item_transfer_new_location',
                            on_delete=models.PROTECT,
                            blank=False,
                            null=False
    )
    add_move = models.ForeignKey(
                            'ItemMove',
                            verbose_name=_('Add Move'),
                            limit_choices_to={
                                    'type': ItemMove.ADD,
                                    'related_to': ItemMove.TRANSFER},
                            related_name='item_move_transfer_add',
                            on_delete=models.PROTECT,
                            blank=False,
                            null=False
    )
    remove_move = models.ForeignKey(
                            'ItemMove',
                            verbose_name=_('Remove Move'),
                            limit_choices_to={
                                    'type': ItemMove.REMOVE,
                                    'related_to': ItemMove.TRANSFER},
                            related_name='item_move_transfer_remove',
                            on_delete=models.PROTECT,
                            blank=False,
                            null=False
    )
    edited_at = models.DateTimeField(
                            verbose_name=_('Edited at'),
                            null=True,
                            blank=True
    )
    created_at = models.DateTimeField(
                            verbose_name=_('Created at'),
                            auto_now_add=True,
                            blank=False
    )

    def edited(self):
        '''
        Edit item transfer
        '''
        self.edited_at = timezone.now()
        self.save()

    def __str__(self):
        '''
        String representation for the record
        '''
        return f"{self.item.code}-({self.old_location}-{self.new_location})"


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
def auto_delete_file_on_change(sender, instance, **kwargs):
    '''
    Deletes old file from filesystem
    when corresponding `Item` object is updated
    with new file.
    '''
    if instance.pk:
        old_photo = Item.objects.get(pk=instance.pk).photo
        new_photo = instance.photo
        if not old_photo == new_photo and old_photo and \
                os.path.isfile(old_photo.path):
            os.remove(old_photo.path)


@receiver(models.signals.pre_save, sender=ItemMove)
def auto_delete_moves_on_change(sender, instance, **kwargs):
    '''
    Deletes old assembly moves when corresponding `ItemMove` object is updated
    with not assmbly item.
    '''
    if instance.pk:
        old_move = ItemMove.objects.get(id=instance.id)
        if not instance.item == old_move.item and old_move.item.is_assembly:
            moves_values = instance.assembly_move_assembly_move.get(
                                id=old_move.id).item_moves.values_list(
                                                            'id', flat=True)
            item_moves = ItemMove.objects.filter(id__in=moves_values)
            for item_move in item_moves:
                item_move.delete()
