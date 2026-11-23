from django.test import TestCase
from django.urls import reverse

from seshat.testing import create_user, create_superuser, create_stock, add_quantity
from stock.models import Location, SubLocation


class LocationViewsTest(TestCase):
    '''
    Test the location and sub-location views
    '''

    def setUp(self):
        self.client.force_login(create_superuser())
        self.location = Location.objects.create(name='MAIN')

    def test_create_location(self):
        response = self.client.post(reverse('stock:NewLocation'), {'name': 'annex'})
        location = Location.objects.get(name='ANNEX')
        self.assertRedirects(response, reverse('stock:LocationDetails', kwargs={'pk': location.pk}))

    def test_edit_location(self):
        self.client.post(reverse('stock:EditLocation', kwargs={'pk': self.location.pk}), {'name': 'hq'})
        self.location.refresh_from_db()
        self.assertEqual(self.location.name, 'HQ')

    def test_list_and_details(self):
        SubLocation.objects.create(location=self.location, name='A1')
        self.assertContains(self.client.get(reverse('stock:LocationsList')), 'A1')
        self.assertContains(self.client.get(
                reverse('stock:LocationDetails', kwargs={'pk': self.location.pk})), 'A1')

    def test_delete_location(self):
        response = self.client.post(reverse('stock:DeleteLocation', kwargs={'pk': self.location.pk}))
        self.assertRedirects(response, reverse('stock:LocationsList'))
        self.assertFalse(Location.objects.exists())

    def test_delete_location_with_sub_locations(self):
        SubLocation.objects.create(location=self.location, name='A1')
        response = self.client.post(reverse('stock:DeleteLocation', kwargs={'pk': self.location.pk}))
        self.assertTemplateUsed(response, 'error_message.html')

    def test_new_sub_location_preselects_location(self):
        response = self.client.get(reverse('stock:NewSubLocation'), {'location': self.location.pk})
        self.assertEqual(str(response.context['form'].initial['location']), str(self.location.pk))
        response = self.client.post(reverse('stock:NewSubLocation'),
                                    {'location': self.location.pk, 'name': 'b2'})
        sub = SubLocation.objects.get(name='B2')
        self.assertRedirects(response, reverse('stock:SubLocationDetails', kwargs={'pk': sub.pk}))

    def test_edit_sub_location(self):
        sub = SubLocation.objects.create(location=self.location, name='A1')
        self.client.post(reverse('stock:EditSubLocation', kwargs={'pk': sub.pk}),
                         {'location': self.location.pk, 'name': 'a9'})
        sub.refresh_from_db()
        self.assertEqual(sub.name, 'A9')

    def test_sub_locations_list_filter(self):
        other = Location.objects.create(name='OTHER')
        SubLocation.objects.create(location=self.location, name='A1')
        SubLocation.objects.create(location=other, name='Z1')
        response = self.client.get(reverse('stock:SubLocationsList'), {'location': other.pk})
        self.assertEqual([s.name for s in response.context['object_list']], ['Z1'])

    def test_sub_location_details_quantities(self):
        item = create_stock()
        add_quantity(item, 7)
        response = self.client.get(reverse('stock:SubLocationDetails', kwargs={'pk': item.location.pk}))
        self.assertEqual(response.context['items_list'], [(item, 7)])

    def test_delete_sub_location(self):
        sub = SubLocation.objects.create(location=self.location, name='A1')
        response = self.client.post(reverse('stock:DeleteSubLocation', kwargs={'pk': sub.pk}))
        self.assertRedirects(response, reverse('stock:SubLocationsList'))

    def test_delete_used_sub_location(self):
        item = create_stock()
        response = self.client.post(reverse('stock:DeleteSubLocation', kwargs={'pk': item.location.pk}))
        self.assertTemplateUsed(response, 'error_message.html')

    def test_permissions(self):
        self.client.force_login(create_user(permissions=['stock.view_item']))
        self.assertEqual(self.client.get(reverse('stock:LocationsList')).status_code, 200)
        for name in ['stock:NewLocation', 'stock:NewSubLocation']:
            self.assertEqual(self.client.get(reverse(name)).status_code, 403)
