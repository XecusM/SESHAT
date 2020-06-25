from django.test import TestCase
from django.urls import reverse, resolve

from stock import views


class StockUrlsTest(TestCase):
    '''
    Test all urls in the stock applciation
    '''
    def test_stock_index_resolved(self):
        '''
        Test stock index url
        '''
        url = reverse('stock:index')
        self.assertEquals(
                        resolve(url).func.view_class,
                        views.Index)

    def test_new_category_resolved(self):
        '''
        Test new category url
        '''
        url = reverse('stock:category_new')
        self.assertEquals(
                        resolve(url).func.view_class,
                        views.CreateCategory)

    def test_edit_category_resolved(self):
        '''
        Test edit category url
        '''
        url = reverse('stock:category_edit', kwargs={'pk': 1})
        self.assertEquals(
                        resolve(url).func.view_class,
                        views.EditCategory)

    def test_categories_list_resolved(self):
        '''
        Test list categories url
        '''
        url = reverse('stock:categories_list')
        self.assertEquals(
                        resolve(url).func.view_class,
                        views.CategoriesList)

    def test_delete_category_resolved(self):
        '''
        Test delete category url
        '''
        url = reverse('stock:category_delete', kwargs={'pk': 1})
        self.assertEquals(
                        resolve(url).func,
                        views.category_delete)

    def test_new_location_resolved(self):
        '''
        Test new location url
        '''
        url = reverse('stock:location_new')
        self.assertEquals(
                        resolve(url).func.view_class,
                        views.CreateLocation)

    def test_edit_location_resolved(self):
        '''
        Test edit location url
        '''
        url = reverse('stock:location_edit', kwargs={'pk': 1})
        self.assertEquals(
                        resolve(url).func.view_class,
                        views.EditLocation)

    def test_locations_list_resolved(self):
        '''
        Test list locations url
        '''
        url = reverse('stock:locations_list')
        self.assertEquals(
                        resolve(url).func.view_class,
                        views.LocationsList)

    def test_delete_location_resolved(self):
        '''
        Test delete location url
        '''
        url = reverse('stock:location_delete', kwargs={'pk': 1})
        self.assertEquals(
                        resolve(url).func,
                        views.location_delete)

    def test_new_sublocation_resolved(self):
        '''
        Test new sub-location url
        '''
        url = reverse('stock:sublocation_new')
        self.assertEquals(
                        resolve(url).func.view_class,
                        views.CreateSubLocation)

    def test_edit_sublocation_resolved(self):
        '''
        Test edit sub-location url
        '''
        url = reverse('stock:sublocation_edit', kwargs={'pk': 1})
        self.assertEquals(
                        resolve(url).func.view_class,
                        views.EditSubLocation)

    def test_sublocations_list_resolved(self):
        '''
        Test list sub-locations url
        '''
        url = reverse('stock:sublocations_list')
        self.assertEquals(
                        resolve(url).func.view_class,
                        views.SubLocationsList)

    def test_delete_sublocation_resolved(self):
        '''
        Test delete sub-location url
        '''
        url = reverse('stock:sublocation_delete', kwargs={'pk': 1})
        self.assertEquals(
                        resolve(url).func,
                        views.sublocation_delete)

    def test_new_item_resolved(self):
        '''
        Test new item url
        '''
        url = reverse('stock:item_new')
        self.assertEquals(
                        resolve(url).func.view_class,
                        views.CreateItem)

    def test_edit_item_resolved(self):
        '''
        Test edit item url
        '''
        url = reverse('stock:item_edit', kwargs={'pk': 1})
        self.assertEquals(
                        resolve(url).func.view_class,
                        views.EditItem)

    def test_item_details_resolved(self):
        '''
        Test view item details url
        '''
        url = reverse('stock:item_details', kwargs={'pk': 1})
        self.assertEquals(
                        resolve(url).func.view_class,
                        views.ItemDetails)

    def test_items_list_resolved(self):
        '''
        Test list items url
        '''
        url = reverse('stock:items_list')
        self.assertEquals(
                        resolve(url).func.view_class,
                        views.ItemsList)

    def test_delete_item_resolved(self):
        '''
        Test delete item url
        '''
        url = reverse('stock:item_delete', kwargs={'pk': 1})
        self.assertEquals(
                        resolve(url).func,
                        views.item_delete)

    def test_new_move_resolved(self):
        '''
        Test new move url
        '''
        url = reverse('stock:move_new', kwargs={'pk': 1})
        self.assertEquals(
                        resolve(url).func.view_class,
                        views.CreateItemMove)

    def test_moves_list_resolved(self):
        '''
        Test list moves url
        '''
        url = reverse('stock:moves_list', kwargs={'pk': 1})
        self.assertEquals(
                        resolve(url).func.view_class,
                        views.ItemMovesList)

    def test_new_transfer_resolved(self):
        '''
        Test new transfer url
        '''
        url = reverse('stock:transfer_new', kwargs={'pk': 1})
        self.assertEquals(
                        resolve(url).func.view_class,
                        views.CreateItemTransfer)
