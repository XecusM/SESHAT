from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.conf import settings
from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType

from stock import models, views


class StockViewsTests(TestCase):
    '''
    Test all views for stock application
    '''
    def setUp(self):
        '''
        Intiate tests
        '''
        self.user = get_user_model().objects.create_user(
                                                username='user',
                                                password='testpassword')

        self.category = models.Category.objects.create(
                                name='New category')

        self.location = models.Location.objects.create(
                                name='New location')

        self.sub_location = models.SubLocation.objects.create(
                                location=self.location,
                                name='new sublocation')

        self.item = models.Item.objects.create(
                                code='code',
                                category=self.category,
                                location=self.sub_location,
                                price=50)

        self.assembled_item = models.Item.objects.create(
                                code='assembly code',
                                category=self.category,
                                location=self.sub_location,
                                price=50,
                                is_assembly=True)

        self.assembly_item = models.AssemblyItem.objects.create(
                                item=self.assembled_item,
                                sub_item=self.item,
                                quantity=5)

        self.item_move = models.ItemMove.objects.create(
                                item=self.item,
                                location=self.sub_location,
                                type=models.ItemMove.ADD,
                                related_to=models.ItemMove.PURCHASE,
                                quantity=20)

        self.assembled_item_move = models.ItemMove.objects.create(
                                item=self.assembled_item,
                                location=self.sub_location,
                                type=models.ItemMove.REMOVE,
                                related_to=models.ItemMove.SELL,
                                quantity=1)

        self.sub_item_move = models.ItemMove.objects.create(
                                item=self.assembly_item.sub_item,
                                location=self.sub_location,
                                type=models.ItemMove.REMOVE,
                                related_to=models.ItemMove.ASSEMBLY,
                                quantity=self.assembled_item_move.quantity \
                                        * self.assembly_item.quantity)

        self.index_url = reverse('stock:index')

        self.category_new_url = reverse('stock:category_new')
        self.category_edit_url = reverse(
                            'stock:category_edit',
                            kwargs={'pk': self.category.id})
        self.categories_list_url = reverse('stock:categories_list')
        self.category_delete_url = reverse(
                            'stock:category_delete',
                            kwargs={'pk': self.category.id})

        self.location_new_url = reverse('stock:location_new')
        self.location_edit_url = reverse(
                            'stock:location_edit',
                            kwargs={'pk': self.location.id})
        self.locations_list_url = reverse('stock:locations_list')
        self.location_delete_url = reverse(
                            'stock:location_delete',
                            kwargs={'pk': self.location.id})

        self.sub_location_new_url = reverse('stock:sublocation_new')
        self.sub_location_edit_url = reverse(
                            'stock:sublocation_edit',
                            kwargs={'pk': self.sub_location.id})
        self.sub_locations_list_url = reverse('stock:sublocations_list')
        self.sub_location_delete_url = reverse(
                            'stock:sublocation_delete',
                            kwargs={'pk': self.sub_location.id})

        self.item_new_url = reverse('stock:item_new')
        self.item_edit_url = reverse(
                            'stock:item_edit',
                            kwargs={'pk': self.item.id})
        self.item_details_url = reverse(
                            'stock:item_details',
                            kwargs={'pk': self.item.id})
        self.items_list_url = reverse('stock:items_list')
        self.item_delete_url = reverse(
                            'stock:item_delete',
                            kwargs={'pk': self.item.id})

        self.move_new_url = reverse(
                            'stock:move_new',
                            kwargs={'pk': self.item.id})
        self.moves_list_url = reverse(
                            'stock:moves_list',
                            kwargs={'pk': self.item.id})

        self.transfer_new_url = reverse(
                            'stock:transfer_new',
                            kwargs={'pk': self.item.id})

    def test_index_get(self):
        '''
        Test get url for stock index page
        '''
        self.client.force_login(self.user)

        response = self.client.get(self.index_url)

        self.assertEqual(response.status_code, 200)
        self.assertIn('itemmove_list', response.context_data)
        self.assertTemplateUsed(
                                response,
                                'stock/index.html')

    def test_new_category_get(self):
        '''
        Test get url for creating new category
        '''
        content_type = ContentType.objects.get_for_model(
                                                    models.Category)
        permission = Permission.objects.get(
                                    codename='add_category',
                                    content_type=content_type)

        self.user.user_permissions.add(permission)

        self.user.refresh_from_db()

        self.client.force_login(self.user)

        response = self.client.get(self.category_new_url)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(
                                response,
                                'stock/category_new.html')

    def test_new_category_permission(self):
        '''
        Test permissions for creating new category
        '''
        self.client.force_login(self.user)

        response = self.client.get(self.category_new_url)

        self.assertEqual(response.status_code, 403)

    def test_new_category_post(self):
        '''
        Test post url for creating new category
        '''
        content_type = ContentType.objects.get_for_model(
                                                    models.Category)
        permission = Permission.objects.get(
                                    codename='add_category',
                                    content_type=content_type)
        self.user.user_permissions.add(permission)

        self.user.refresh_from_db()

        self.client.force_login(self.user)

        payload = {'name': 'Another category', }

        response = self.client.post(self.category_new_url, data=payload)

        self.assertEqual(response.status_code, 302)
        self.assertEquals(models.Category.objects.all().count(), 2)

    def test_edit_category_get(self):
        '''
        Test get url for creating edit category
        '''
        content_type = ContentType.objects.get_for_model(
                                                    models.Category)
        permission = Permission.objects.get(
                                    codename='change_category',
                                    content_type=content_type)

        self.user.user_permissions.add(permission)

        self.user.refresh_from_db()

        self.client.force_login(self.user)

        response = self.client.get(self.category_edit_url)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(
                                response,
                                'stock/category_edit.html')

    def test_edit_category_permission(self):
        '''
        Test permissions for creating edit category
        '''
        self.client.force_login(self.user)

        response = self.client.get(self.category_edit_url)

        self.assertEqual(response.status_code, 403)

    def test_edit_category_post(self):
        '''
        Test post url for creating edit category
        '''
        content_type = ContentType.objects.get_for_model(
                                                    models.Category)
        permission = Permission.objects.get(
                                    codename='change_category',
                                    content_type=content_type)
        self.user.user_permissions.add(permission)

        self.user.refresh_from_db()

        self.client.force_login(self.user)

        payload = {'name': 'Another category', }

        response = self.client.post(self.category_edit_url, data=payload)

        self.category.refresh_from_db()

        self.assertEqual(response.status_code, 302)
        self.assertEquals(self.category.name, payload['name'])

    def test_categories_list_get(self):
        '''
        Test get url for stock categories list page
        '''
        self.client.force_login(self.user)

        response = self.client.get(self.categories_list_url)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(
                                response,
                                'stock/categories_list.html')

    def test_category_delete_get(self):
        '''
        Test get url for category delete
        '''
        category = models.Category.objects.create(name='D Cateogry')

        content_type = ContentType.objects.get_for_model(models.Category)
        permission = Permission.objects.get(
                                    codename='delete_category',
                                    content_type=content_type)

        self.user.user_permissions.add(permission)

        self.user.refresh_from_db()

        self.client.force_login(self.user)

        response = self.client.get(
                        reverse(
                                'stock:category_delete',
                                kwargs={'pk': category.id}))

        self.assertEqual(response.status_code, 404)

    def test_category_delete_permission(self):
        '''
        Test permissions for category delete
        '''
        category = models.Category.objects.create(name='D Cateogry')

        self.client.force_login(self.user)

        response = self.client.get(
                                reverse(
                                    'stock:category_delete',
                                    kwargs={'pk': category.id}))

        self.assertEqual(response.status_code, 403)

    def test_delete_category_post(self):
        '''
        Test post url for category delete
        '''
        category = models.Category.objects.create(name='D Cateogry')

        content_type = ContentType.objects.get_for_model(models.Category)
        permission = Permission.objects.get(
                                    codename='delete_category',
                                    content_type=content_type)
        self.user.user_permissions.add(permission)

        self.user.refresh_from_db()

        self.client.force_login(self.user)

        self.assertEqual(models.Category.objects.all().count(), 2)

        response = self.client.post(
                                reverse(
                                    'stock:category_delete',
                                    kwargs={'pk': category.id}))

        self.assertEqual(response.status_code, 302)
        self.assertEqual(models.Category.objects.all().count(), 1)

    def test_new_location_get(self):
        '''
        Test get url for creating new location
        '''
        content_type = ContentType.objects.get_for_model(
                                                    models.Location)
        permission = Permission.objects.get(
                                    codename='add_location',
                                    content_type=content_type)

        self.user.user_permissions.add(permission)

        self.user.refresh_from_db()

        self.client.force_login(self.user)

        response = self.client.get(self.location_new_url)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(
                                response,
                                'stock/location_new.html')

    def test_new_location_permission(self):
        '''
        Test permissions for creating new location
        '''
        self.client.force_login(self.user)

        response = self.client.get(self.location_new_url)

        self.assertEqual(response.status_code, 403)

    def test_new_location_post(self):
        '''
        Test post url for creating new location
        '''
        content_type = ContentType.objects.get_for_model(
                                                    models.Location)
        permission = Permission.objects.get(
                                    codename='add_location',
                                    content_type=content_type)
        self.user.user_permissions.add(permission)

        self.user.refresh_from_db()

        self.client.force_login(self.user)

        payload = {'name': 'Another location', }

        response = self.client.post(self.location_new_url, data=payload)

        self.assertEqual(response.status_code, 302)
        self.assertEquals(models.Location.objects.all().count(), 2)

    def test_edit_location_get(self):
        '''
        Test get url for creating edit location
        '''
        content_type = ContentType.objects.get_for_model(
                                                    models.Location)
        permission = Permission.objects.get(
                                    codename='change_location',
                                    content_type=content_type)

        self.user.user_permissions.add(permission)

        self.user.refresh_from_db()

        self.client.force_login(self.user)

        response = self.client.get(self.location_edit_url)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(
                                response,
                                'stock/location_edit.html')

    def test_edit_location_permission(self):
        '''
        Test permissions for creating edit location
        '''
        self.client.force_login(self.user)

        response = self.client.get(self.location_edit_url)

        self.assertEqual(response.status_code, 403)

    def test_edit_location_post(self):
        '''
        Test post url for creating edit location
        '''
        content_type = ContentType.objects.get_for_model(
                                                    models.Location)
        permission = Permission.objects.get(
                                    codename='change_location',
                                    content_type=content_type)
        self.user.user_permissions.add(permission)

        self.user.refresh_from_db()

        self.client.force_login(self.user)

        payload = {'name': 'Another location', }

        response = self.client.post(self.location_edit_url, data=payload)

        self.location.refresh_from_db()

        self.assertEqual(response.status_code, 302)
        self.assertEquals(self.location.name, payload['name'].upper())

    def test_locations_list_get(self):
        '''
        Test get url for stock locations list page
        '''
        self.client.force_login(self.user)

        response = self.client.get(self.locations_list_url)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(
                                response,
                                'stock/locations_list.html')

    def test_location_delete_get(self):
        '''
        Test get url for location delete
        '''
        location = models.Location.objects.create(name='D Location')

        content_type = ContentType.objects.get_for_model(models.Location)
        permission = Permission.objects.get(
                                    codename='delete_location',
                                    content_type=content_type)

        self.user.user_permissions.add(permission)

        self.user.refresh_from_db()

        self.client.force_login(self.user)

        response = self.client.get(
                        reverse(
                                'stock:location_delete',
                                kwargs={'pk': location.id}))

        self.assertEqual(response.status_code, 404)

    def test_location_delete_permission(self):
        '''
        Test permissions for location delete
        '''
        location = models.Location.objects.create(name='D Location')

        self.client.force_login(self.user)

        response = self.client.get(
                                reverse(
                                    'stock:location_delete',
                                    kwargs={'pk': location.id}))

        self.assertEqual(response.status_code, 403)

    def test_delete_location_post(self):
        '''
        Test post url for location delete
        '''
        location = models.Location.objects.create(name='D Location')

        content_type = ContentType.objects.get_for_model(models.Location)
        permission = Permission.objects.get(
                                    codename='delete_location',
                                    content_type=content_type)
        self.user.user_permissions.add(permission)

        self.user.refresh_from_db()

        self.client.force_login(self.user)

        self.assertEqual(models.Location.objects.all().count(), 2)

        response = self.client.post(
                                reverse(
                                    'stock:location_delete',
                                    kwargs={'pk': location.id}))

        self.assertEqual(response.status_code, 302)
        self.assertEqual(models.Location.objects.all().count(), 1)

    def test_new_sublocation_get(self):
        '''
        Test get url for creating new sub-location
        '''
        content_type = ContentType.objects.get_for_model(
                                                    models.SubLocation)
        permission = Permission.objects.get(
                                    codename='add_sublocation',
                                    content_type=content_type)

        self.user.user_permissions.add(permission)

        self.user.refresh_from_db()

        self.client.force_login(self.user)

        response = self.client.get(self.sub_location_new_url)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(
                                response,
                                'stock/sublocation_new.html')

    def test_new_sublocation_permission(self):
        '''
        Test permissions for creating new sub-location
        '''
        self.client.force_login(self.user)

        response = self.client.get(self.sub_location_new_url)

        self.assertEqual(response.status_code, 403)

    def test_new_sublocation_post(self):
        '''
        Test post url for creating new sublocation
        '''
        content_type = ContentType.objects.get_for_model(
                                                    models.SubLocation)
        permission = Permission.objects.get(
                                    codename='add_sublocation',
                                    content_type=content_type)
        self.user.user_permissions.add(permission)

        self.user.refresh_from_db()

        self.client.force_login(self.user)

        payload = {
                    'location': self.location.id,
                    'name': 'Another sublocation',
                }

        response = self.client.post(self.sub_location_new_url, data=payload)

        self.assertEqual(response.status_code, 302)
        self.assertEquals(models.SubLocation.objects.all().count(), 2)

    def test_edit_sublocation_get(self):
        '''
        Test get url for creating edit sub-location
        '''
        content_type = ContentType.objects.get_for_model(
                                                    models.SubLocation)
        permission = Permission.objects.get(
                                    codename='change_sublocation',
                                    content_type=content_type)

        self.user.user_permissions.add(permission)

        self.user.refresh_from_db()

        self.client.force_login(self.user)

        response = self.client.get(self.sub_location_edit_url)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(
                                response,
                                'stock/sublocation_edit.html')

    def test_edit_sublocation_permission(self):
        '''
        Test permissions for creating edit sub-location
        '''
        self.client.force_login(self.user)

        response = self.client.get(self.sub_location_edit_url)

        self.assertEqual(response.status_code, 403)

    def test_edit_sublocation_post(self):
        '''
        Test post url for creating edit sublocation
        '''
        content_type = ContentType.objects.get_for_model(
                                                    models.SubLocation)
        permission = Permission.objects.get(
                                    codename='change_sublocation',
                                    content_type=content_type)
        self.user.user_permissions.add(permission)

        self.user.refresh_from_db()

        self.client.force_login(self.user)

        payload = {
                    'location': self.location.id,
                    'name': 'Another sublocation',
                }

        response = self.client.post(self.sub_location_edit_url, data=payload)

        self.sub_location.refresh_from_db()

        self.assertEqual(response.status_code, 302)
        self.assertEquals(self.sub_location.name, payload['name'].upper())

    def test_sublocations_list_get(self):
        '''
        Test get url for stock sub-locations list page
        '''
        self.client.force_login(self.user)

        response = self.client.get(self.sub_locations_list_url)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(
                                response,
                                'stock/sublocations_list.html')

    def test_sublocation_delete_get(self):
        '''
        Test get url for sublocation delete
        '''
        sublocation = models.SubLocation.objects.create(
                                            location=self.location,
                                            name='D SubLocation')

        content_type = ContentType.objects.get_for_model(models.SubLocation)
        permission = Permission.objects.get(
                                    codename='delete_sublocation',
                                    content_type=content_type)

        self.user.user_permissions.add(permission)

        self.user.refresh_from_db()

        self.client.force_login(self.user)

        response = self.client.get(
                        reverse(
                                'stock:sublocation_delete',
                                kwargs={'pk': sublocation.id}))

        self.assertEqual(response.status_code, 404)

    def test_sublocation_delete_permission(self):
        '''
        Test permissions for sublocation delete
        '''
        sublocation = models.SubLocation.objects.create(
                                            location=self.location,
                                            name='D SubLocation')

        self.client.force_login(self.user)

        response = self.client.get(
                                reverse(
                                    'stock:sublocation_delete',
                                    kwargs={'pk': sublocation.id}))

        self.assertEqual(response.status_code, 403)

    def test_delete_sublocation_post(self):
        '''
        Test post url for sublocation delete
        '''
        sublocation = models.SubLocation.objects.create(
                                            location=self.location,
                                            name='D SubLocation')

        content_type = ContentType.objects.get_for_model(models.SubLocation)
        permission = Permission.objects.get(
                                    codename='delete_sublocation',
                                    content_type=content_type)
        self.user.user_permissions.add(permission)

        self.user.refresh_from_db()

        self.client.force_login(self.user)

        self.assertEqual(models.SubLocation.objects.all().count(), 2)

        response = self.client.post(
                                reverse(
                                    'stock:sublocation_delete',
                                    kwargs={'pk': sublocation.id}))

        self.assertEqual(response.status_code, 302)
        self.assertEqual(models.SubLocation.objects.all().count(), 1)

    def test_new_item_get(self):
        '''
        Test get url for creating new item
        '''
        content_type = ContentType.objects.get_for_model(
                                                    models.Item)
        permission = Permission.objects.get(
                                    codename='add_item',
                                    content_type=content_type)

        self.user.user_permissions.add(permission)

        self.user.refresh_from_db()

        self.client.force_login(self.user)

        response = self.client.get(self.item_new_url)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(
                                response,
                                'stock/item_new.html')

    def test_new_item_permission(self):
        '''
        Test permissions for creating new item
        '''
        self.client.force_login(self.user)

        response = self.client.get(self.item_new_url)

        self.assertEqual(response.status_code, 403)

    def test_new_item_post(self):
        '''
        Test post url for creating new item
        '''
        content_type = ContentType.objects.get_for_model(
                                                    models.Item)
        permission = Permission.objects.get(
                                    codename='add_item',
                                    content_type=content_type)
        self.user.user_permissions.add(permission)

        self.user.refresh_from_db()

        self.client.force_login(self.user)

        payload = {
                    'code': 'code20',
                    'location': self.sub_location.id,
                    'price': 50,
                    'category': self.category.id
                }

        response = self.client.post(self.item_new_url, data=payload)

        self.assertEqual(response.status_code, 302)
        self.assertEquals(models.Item.objects.all().count(), 3)

    def test_new_assembly_item_post(self):
        '''
        Test post url for creating new assembly_item
        '''
        content_type = ContentType.objects.get_for_model(
                                                    models.Item)
        permission = Permission.objects.get(
                                    codename='add_item',
                                    content_type=content_type)
        self.user.user_permissions.add(permission)

        self.user.refresh_from_db()

        self.client.force_login(self.user)

        payload = {
                    'code': 'code20',
                    'location': self.sub_location.id,
                    'price': 50,
                    'category': self.category.id,
                    'is_assembly': 'on',
                    'items': 1,
                    '1sub_item': self.item.id,
                    '1quantity': 5
                }

        response = self.client.post(self.item_new_url, data=payload)

        self.assertEqual(response.status_code, 302)
        self.assertEquals(models.Item.objects.all().count(), 3)
        self.assertEquals(models.AssemblyItem.objects.all().count(), 2)

    def test_edit_item_get(self):
        '''
        Test get url for creating edit item
        '''
        content_type = ContentType.objects.get_for_model(
                                                    models.Item)
        permission = Permission.objects.get(
                                    codename='change_item',
                                    content_type=content_type)

        self.user.user_permissions.add(permission)

        self.user.refresh_from_db()

        self.client.force_login(self.user)

        response = self.client.get(self.item_edit_url)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(
                                response,
                                'stock/item_edit.html')

    def test_edit_item_permission(self):
        '''
        Test permissions for creating edit item
        '''
        self.client.force_login(self.user)

        response = self.client.get(self.item_edit_url)

        self.assertEqual(response.status_code, 403)

    def test_edit_item_post(self):
        '''
        Test post url for creating edit item
        '''
        content_type = ContentType.objects.get_for_model(
                                                    models.Item)
        permission = Permission.objects.get(
                                    codename='change_item',
                                    content_type=content_type)
        self.user.user_permissions.add(permission)

        self.user.refresh_from_db()

        self.client.force_login(self.user)

        payload = {
                    'code': 'code20',
                    'location': self.sub_location.id,
                    'price': 50,
                    'category': self.category.id
                }

        response = self.client.post(self.item_edit_url, data=payload)

        self.item.refresh_from_db()

        self.assertEqual(response.status_code, 302)
        self.assertEquals(self.item.code, payload['code'].upper())

    def test_edit_assembly_item_post(self):
        '''
        Test post url for creating edit assembly_item
        '''
        content_type = ContentType.objects.get_for_model(
                                                    models.Item)
        permission = Permission.objects.get(
                                    codename='change_item',
                                    content_type=content_type)
        self.user.user_permissions.add(permission)

        self.user.refresh_from_db()

        self.client.force_login(self.user)

        payload = {
                    'code': 'code20',
                    'location': self.sub_location.id,
                    'price': 50,
                    'category': self.category.id,
                    'is_assembly': 'on',
                    'items': 1,
                    '1sub_item': self.item.id,
                    '1quantity': 5
                }

        response = self.client.post(
                            reverse(
                                    'stock:item_edit',
                                    kwargs={'pk': self.assembled_item.id}),
                            data=payload)
        self.assembled_item.refresh_from_db()

        self.assertEqual(response.status_code, 302)
        self.assertEquals(self.assembled_item.code, payload['code'].upper())

    def test_item_details_get(self):
        '''
        Test get url for item details
        '''
        self.client.force_login(self.user)

        response = self.client.get(self.item_details_url)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(
                                response,
                                'stock/item_details.html')

    def test_items_list_get(self):
        '''
        Test get url for stock items list page
        '''
        self.client.force_login(self.user)

        response = self.client.get(self.items_list_url)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(
                                response,
                                'stock/items_list.html')

    def test_item_delete_get(self):
        '''
        Test get url for item delete
        '''
        item = models.Item.objects.create(
                                code='codeD',
                                category=self.category,
                                location=self.sub_location,
                                price=50)

        content_type = ContentType.objects.get_for_model(
                                                    models.Item)
        permission = Permission.objects.get(
                                    codename='delete_item',
                                    content_type=content_type)

        self.user.user_permissions.add(permission)

        self.user.refresh_from_db()

        self.client.force_login(self.user)

        response = self.client.get(
                        reverse('stock:item_delete', kwargs={'pk': item.id}))

        self.assertEqual(response.status_code, 404)

    def test_item_delete_permission(self):
        '''
        Test permissions for item delete
        '''
        item = models.Item.objects.create(
                                code='codeD',
                                category=self.category,
                                location=self.sub_location,
                                price=50)

        self.client.force_login(self.user)

        response = self.client.get(
                        reverse('stock:item_delete', kwargs={'pk': item.id}))

        self.assertEqual(response.status_code, 403)

    def test_delete_item_post(self):
        '''
        Test post url for item delete
        '''
        item = models.Item.objects.create(
                                code='codeD',
                                category=self.category,
                                location=self.sub_location,
                                price=50)

        content_type = ContentType.objects.get_for_model(
                                                    models.Item)
        permission = Permission.objects.get(
                                    codename='delete_item',
                                    content_type=content_type)
        self.user.user_permissions.add(permission)

        self.user.refresh_from_db()

        self.client.force_login(self.user)

        self.assertEqual(models.Item.objects.all().count(), 3)

        response = self.client.post(
                        reverse('stock:item_delete', kwargs={'pk': item.id}))

        self.assertEqual(response.status_code, 302)
        self.assertEqual(models.Item.objects.all().count(), 2)

    def test_new_move_get(self):
        '''
        Test get url for creating new move
        '''
        content_type = ContentType.objects.get_for_model(
                                                    models.ItemMove)
        permission = Permission.objects.get(
                                    codename='add_itemmove',
                                    content_type=content_type)

        self.user.user_permissions.add(permission)

        self.user.refresh_from_db()

        self.client.force_login(self.user)

        response = self.client.get(self.move_new_url)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(
                                response,
                                'stock/move_new.html')

    def test_new_move_permission(self):
        '''
        Test permissions for creating new move
        '''
        self.client.force_login(self.user)

        response = self.client.get(self.move_new_url)

        self.assertEqual(response.status_code, 403)

    def test_new_move_post(self):
        '''
        Test post url for creating new move
        '''
        content_type = ContentType.objects.get_for_model(
                                                    models.ItemMove)
        permission = Permission.objects.get(
                                    codename='add_itemmove',
                                    content_type=content_type)
        self.user.user_permissions.add(permission)

        self.user.refresh_from_db()

        self.client.force_login(self.user)

        payload = {
                    'item': self.item.id,
                    'location': self.sub_location.id,
                    'type': models.ItemMove.ADD,
                    'related_to': models.ItemMove.CUSTOM,
                    'quantity': 5,
                    'note': 'New Test'
                }

        response = self.client.post(self.move_new_url, data=payload)

        self.assertEqual(response.status_code, 302)
        self.assertEquals(models.ItemMove.objects.all().count(), 5)

    def test_moves_list_get(self):
        '''
        Test get url for item moves list page
        '''
        self.client.force_login(self.user)

        response = self.client.get(self.moves_list_url)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(
                                response,
                                'stock/moves_list.html')

    def test_new_transfer_get(self):
        '''
        Test get url for creating new transfer
        '''
        content_type = ContentType.objects.get_for_model(
                                                    models.ItemTransfer)
        permission = Permission.objects.get(
                                    codename='add_itemtransfer',
                                    content_type=content_type)

        self.user.user_permissions.add(permission)

        self.user.refresh_from_db()

        self.client.force_login(self.user)

        response = self.client.get(self.transfer_new_url)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(
                                response,
                                'stock/transfer_new.html')

    def test_new_transfer_permission(self):
        '''
        Test permissions for creating new transfer
        '''
        self.client.force_login(self.user)

        response = self.client.get(self.transfer_new_url)

        self.assertEqual(response.status_code, 403)

    def test_new_transfer_post(self):
        '''
        Test post url for creating new transfer
        '''
        new_location = models.SubLocation.objects.create(
                                location=self.location,
                                name='another sublocation')

        content_type = ContentType.objects.get_for_model(
                                                    models.ItemTransfer)
        permission = Permission.objects.get(
                                    codename='add_itemtransfer',
                                    content_type=content_type)
        self.user.user_permissions.add(permission)

        self.user.refresh_from_db()

        self.client.force_login(self.user)

        payload = {
                    'item': self.item.id,
                    'old_location': self.sub_location.id,
                    'new_location': new_location.id,
                    'quantity': 1,
                    'note': 'New Test'
                }

        response = self.client.post(self.transfer_new_url, data=payload)

        self.assertEqual(response.status_code, 302)
        self.assertEquals(models.ItemMove.objects.all().count(), 6)
