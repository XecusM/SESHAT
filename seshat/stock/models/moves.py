from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator
from django.db import models, transaction
from django.utils.translation import gettext_lazy as _

from x_django_app.models import XModel

from .items import moves_balance


class ItemMove(models.Model, XModel):
    '''
    Model for the movements done on the items: every add or remove of
    quantity in a sub-location is an item move
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
    quantity = models.PositiveIntegerField(
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
    created_at = models.DateTimeField(
                            verbose_name=_('Created at'),
                            auto_now_add=True,
                            blank=False
    )

    class Meta:
        verbose_name = _('Item move')
        verbose_name_plural = _('Item moves')
        ordering = ('-created_at', '-id')

    @property
    def signed_quantity(self):
        '''
        The quantity as a positive (add) or negative (remove) number
        '''
        return self.quantity if self.type == self.ADD else -self.quantity

    def _balance_without_self(self, item, location):
        '''
        The item balance in the location, ignoring this move
        '''
        moves = item.item_move_item.filter(location=location)
        if self.pk:
            moves = moves.exclude(pk=self.pk)
        return moves_balance(moves)

    def validate_stock(self):
        '''
        Raise ValidationError when saving this move makes a quantity negative
        '''
        if not self.item.is_assembly:
            balance = self._balance_without_self(self.item, self.location)
            if balance + self.signed_quantity < 0:
                raise ValidationError(
                    _("Quantity can't be negative for the selected location "
                      "(%(item)s: %(available)s available)"),
                    code='negative_quantity',
                    params={'item': self.item.code, 'available': balance})

        if self.pk:
            old = ItemMove.objects.select_related('item').get(pk=self.pk)
            if (old.item_id, old.location_id) != (
                                    self.item_id, self.location_id) \
                    and not old.item.is_assembly:
                if self._balance_without_self(old.item, old.location) < 0:
                    raise ValidationError(
                        _("Quantity can't be negative for the selected "
                          "location (%(item)s)"),
                        code='negative_quantity',
                        params={'item': old.item.code})

    def save(self, *args, **kwargs):
        '''
        Save the move after checking the stock. Moves of an assembled item
        also move its components.
        '''
        with transaction.atomic():
            old_item = None
            if self.pk:
                old_item = ItemMove.objects.select_related(
                                                'item').get(pk=self.pk).item
            self.validate_stock()
            super().save(*args, **kwargs)
            if old_item is not None and old_item.is_assembly \
                    and old_item != self.item:
                self.delete_component_moves()
            if self.item.is_assembly:
                self.sync_component_moves()

    def sync_component_moves(self):
        '''
        Create or update the component moves of an assembled item move
        '''
        assembly_move, _created = AssemblyMove.objects.get_or_create(
                                                        assembly_move=self)
        existing = {
            move.item_id: move for move in assembly_move.item_moves.all()}
        components = list(self.item.get_assembly_items())
        if not components:
            raise ValidationError(
                    _("Can't find items for the assembled item"),
                    code='no_components')

        for component in components:
            move = existing.pop(component.sub_item_id, None)
            if move is None:
                move = ItemMove(
                            item=component.sub_item,
                            related_to=ItemMove.ASSEMBLY)
            move.location = component.sub_item.location
            move.type = self.type
            move.quantity = self.quantity * component.quantity
            move.note = f"{self.item.code}"
            move.save()
            assembly_move.item_moves.add(move)

        for move in existing.values():
            assembly_move.item_moves.remove(move)
            move.delete()

    def delete_component_moves(self):
        '''
        Delete the component moves of an assembled item move
        '''
        assembly_move = AssemblyMove.objects.filter(assembly_move=self).first()
        if assembly_move is not None:
            assembly_move.delete()

    def delete(self, *args, **kwargs):
        '''
        Delete the move after checking the stock
        '''
        with transaction.atomic():
            if self.item.is_assembly:
                self.delete_component_moves()
            elif self.type == self.ADD:
                if self._balance_without_self(self.item, self.location) < 0:
                    raise ValidationError(
                        _("Can't delete this move, the quantity would "
                          "become negative (%(item)s)"),
                        code='negative_quantity',
                        params={'item': self.item.code})
            return super().delete(*args, **kwargs)

    def __str__(self):
        '''
        String representation for the record
        '''
        return f"{self.get_type_display()}-{self.id}"


class AssemblyMove(models.Model):
    '''
    Link the move of an assembled item to its components' moves
    '''
    assembly_move = models.OneToOneField(
                            'ItemMove',
                            verbose_name=_('Item move'),
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
    created_at = models.DateTimeField(
                            verbose_name=_('Created at'),
                            auto_now_add=True,
                            blank=False
    )

    def delete(self, *args, **kwargs):
        '''
        Delete the components' moves too
        '''
        with transaction.atomic():
            item_moves = list(self.item_moves.all())
            result = super().delete(*args, **kwargs)
            for item_move in item_moves:
                item_move.delete()
            return result

    def __str__(self):
        '''
        String representation for the record
        '''
        return f"{self.assembly_move.item.code}-{self.id}"


class ItemTransfer(models.Model, XModel):
    '''
    Model for transfer item from a sub-location to another
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
                            verbose_name=_('From Location'),
                            related_name='item_transfer_old_location',
                            on_delete=models.PROTECT,
                            blank=False,
                            null=False
    )
    new_location = models.ForeignKey(
                            'SubLocation',
                            verbose_name=_('To Location'),
                            related_name='item_transfer_new_location',
                            on_delete=models.PROTECT,
                            blank=False,
                            null=False
    )
    add_move = models.OneToOneField(
                            'ItemMove',
                            verbose_name=_('Add Move'),
                            related_name='item_move_transfer_add',
                            on_delete=models.PROTECT,
                            blank=False,
                            null=False
    )
    remove_move = models.OneToOneField(
                            'ItemMove',
                            verbose_name=_('Remove Move'),
                            related_name='item_move_transfer_remove',
                            on_delete=models.PROTECT,
                            blank=False,
                            null=False
    )
    created_at = models.DateTimeField(
                            verbose_name=_('Created at'),
                            auto_now_add=True,
                            blank=False
    )

    class Meta:
        verbose_name = _('Item transfer')
        verbose_name_plural = _('Item transfers')

    @property
    def quantity(self):
        '''
        The transferred quantity
        '''
        return self.add_move.quantity

    @classmethod
    def transfer(cls, item, old_location, new_location, quantity, note=None):
        '''
        Move the quantity of the item from old_location to new_location
        '''
        if old_location == new_location:
            raise ValidationError(
                    _("The two locations must be different"),
                    code='same_location')
        with transaction.atomic():
            remove_move = ItemMove.objects.create(
                                item=item,
                                location=old_location,
                                type=ItemMove.REMOVE,
                                quantity=quantity,
                                related_to=ItemMove.TRANSFER,
                                note=note)
            add_move = ItemMove.objects.create(
                                item=item,
                                location=new_location,
                                type=ItemMove.ADD,
                                quantity=quantity,
                                related_to=ItemMove.TRANSFER,
                                note=note)
            return cls.objects.create(
                                item=item,
                                old_location=old_location,
                                new_location=new_location,
                                add_move=add_move,
                                remove_move=remove_move)

    def __str__(self):
        '''
        String representation for the record
        '''
        return f"{self.item.code}-({self.old_location}-{self.new_location})"
