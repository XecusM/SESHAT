from django.test import TestCase
from django.urls import reverse

from x_django_app.models import XActivity

from seshat.testing import create_user, create_superuser, create_stock
from stock.models import Category


class CategoryViewsTest(TestCase):
    '''
    Test the category views
    '''

    def setUp(self):
        self.client.force_login(create_superuser())

    def test_list_and_search(self):
        Category.objects.create(name='Bolts')
        Category.objects.create(name='Nuts')
        response = self.client.get(reverse('stock:CategoriesList'), {'search': 'bol'})
        self.assertEqual([c.name for c in response.context['object_list']], ['Bolts'])

    def test_create(self):
        response = self.client.post(reverse('stock:NewCategory'), {'name': 'glue'})
        category = Category.objects.get(name='Glue')
        self.assertRedirects(response, reverse('stock:CategoryDetails', kwargs={'pk': category.pk}))
        self.assertEqual(category.get_activities().first().activity, XActivity.CREATE)

    def test_create_next(self):
        response = self.client.post(
                    reverse('stock:NewCategory') + '?next=/stock/items/', {'name': 'tape'})
        self.assertEqual(response.url, '/stock/items/')

    def test_edit(self):
        category = Category.objects.create(name='Old')
        self.client.post(reverse('stock:EditCategory', kwargs={'pk': category.pk}), {'name': 'new'})
        category.refresh_from_db()
        self.assertEqual(category.name, 'New')

    def test_details(self):
        item = create_stock()
        response = self.client.get(reverse('stock:CategoryDetails', kwargs={'pk': item.category.pk}))
        self.assertContains(response, item.code)

    def test_delete(self):
        category = Category.objects.create(name='Gone')
        response = self.client.post(reverse('stock:DeleteCategory', kwargs={'pk': category.pk}))
        self.assertRedirects(response, reverse('stock:CategoriesList'))
        self.assertFalse(Category.objects.filter(pk=category.pk).exists())

    def test_delete_used_category(self):
        item = create_stock()
        response = self.client.post(reverse('stock:DeleteCategory', kwargs={'pk': item.category.pk}))
        self.assertTemplateUsed(response, 'error_message.html')
        self.assertTrue(Category.objects.filter(pk=item.category.pk).exists())

    def test_permissions(self):
        category = Category.objects.create(name='Locked')
        self.client.force_login(create_user(permissions=['stock.view_item']))
        self.assertEqual(self.client.get(reverse('stock:CategoriesList')).status_code, 200)
        self.assertEqual(self.client.get(reverse('stock:NewCategory')).status_code, 403)
        self.assertEqual(self.client.get(
                reverse('stock:EditCategory', kwargs={'pk': category.pk})).status_code, 403)
        self.assertEqual(self.client.post(
                reverse('stock:DeleteCategory', kwargs={'pk': category.pk})).status_code, 403)
        self.client.force_login(create_user('none'))
        self.assertEqual(self.client.get(reverse('stock:CategoriesList')).status_code, 403)
