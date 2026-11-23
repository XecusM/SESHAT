from django.db import models
from django.utils.translation import gettext_lazy as _

from x_django_app.models import XModel


class Category(models.Model, XModel):
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
    created_at = models.DateTimeField(
                        verbose_name=_('Created at'),
                        auto_now_add=True,
                        blank=False
    )

    class Meta:
        verbose_name = _('Category')
        verbose_name_plural = _('Categories')
        ordering = ('name', )

    def clean(self):
        '''
        Change cleaned data before save to database
        '''
        self.name = str(self.name).strip().capitalize()

    def get_items(self):
        '''
        Get all items for selected category
        '''
        return self.item_category.all().order_by('code')

    def can_be_deleted(self):
        '''
        A category with items can't be deleted
        '''
        return not self.item_category.exists()

    def __str__(self):
        '''
        String representation for the record
        '''
        return self.name
