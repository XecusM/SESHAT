from django.test import TestCase

from seshat.testing import create_stock, add_quantity
from stock.models import Location, SubLocation


class LocationModelTest(TestCase):
    '''
    Test the location model
    '''

    def test_clean_uppercases(self):
        location = Location(name=' store ')
        location.clean()
        self.assertEqual(location.name, 'STORE')

    def test_sub_locations_and_delete_check(self):
        location = Location.objects.create(name='STORE')
        self.assertTrue(location.can_be_deleted())
        SubLocation.objects.create(location=location, name='B')
        SubLocation.objects.create(location=location, name='A')
        self.assertEqual([s.name for s in location.get_sub_locations()], ['A', 'B'])
        self.assertFalse(location.can_be_deleted())
        self.assertEqual(str(location), 'STORE')


class SubLocationModelTest(TestCase):
    '''
    Test the sub-location model
    '''

    def test_str_and_clean(self):
        sub = SubLocation(location=Location.objects.create(name='MAIN'), name='a1')
        sub.clean()
        self.assertEqual(str(sub), 'MAIN / A1')

    def test_items_and_delete_check(self):
        item = create_stock()
        sub = item.location
        other = SubLocation.objects.create(location=sub.location, name='EMPTY')
        self.assertTrue(other.can_be_deleted())
        self.assertFalse(sub.can_be_deleted())
        add_quantity(item, 3, other)
        self.assertEqual(list(other.get_items()), [item])
        self.assertFalse(other.can_be_deleted())
