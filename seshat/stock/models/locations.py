from django.db import models
from django.utils.translation import gettext_lazy as _

from x_django_app.models import XModel


class Location(models.Model, XModel):
    '''
    Model for item locations to store (e.g. a warehouse)
    '''
    name = models.CharField(
                            verbose_name=_('Location name'),
                            max_length=128,
                            unique=True,
                            blank=False,
                            null=False
    )
    created_at = models.DateTimeField(
                            verbose_name=_('Created at'),
                            auto_now_add=True,
                            blank=False
    )

    class Meta:
        verbose_name = _('Location')
        verbose_name_plural = _('Locations')
        ordering = ('name', )

    def clean(self):
        '''
        Change cleaned data before save to database
        '''
        self.name = str(self.name).strip().upper()

    def get_sub_locations(self):
        '''
        Get all sub-locations for selected location
        '''
        return self.sub_location.all().order_by('name')

    def can_be_deleted(self):
        '''
        A location with sub-locations can't be deleted
        '''
        return not self.sub_location.exists()

    def __str__(self):
        '''
        String representation for the record
        '''
        return self.name


class SubLocation(models.Model, XModel):
    '''
    Model for item sub-locations to store (e.g. a shelf in a warehouse)
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
    created_at = models.DateTimeField(
                            verbose_name=_('Created at'),
                            auto_now_add=True,
                            blank=False
    )

    class Meta:
        verbose_name = _('Sub-location')
        verbose_name_plural = _('Sub-locations')
        ordering = ('location__name', 'name')

    def clean(self):
        '''
        Change cleaned data before save to database
        '''
        self.name = str(self.name).strip().upper()

    def get_items(self):
        '''
        return all items that moved through this sub-location
        '''
        from .items import Item
        return Item.objects.filter(
                        item_move_item__location=self).distinct().order_by('code')

    def can_be_deleted(self):
        '''
        A sub-location used by items or moves can't be deleted
        '''
        return not (self.item_location.exists()
                    or self.item_move_location.exists())

    def __str__(self):
        '''
        String representation for the record
        '''
        return f"{self.location.name} / {self.name}"
