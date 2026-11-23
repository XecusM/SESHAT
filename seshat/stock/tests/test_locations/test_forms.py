from django.test import TestCase

from stock.forms import LocationForm, SubLocationForm
from stock.models import Location


class LocationFormsTest(TestCase):
    '''
    Test the location forms
    '''

    def test_location_form(self):
        form = LocationForm(data={'name': 'depot'})
        self.assertTrue(form.is_valid())
        self.assertEqual(form.save().name, 'DEPOT')

    def test_sub_location_form(self):
        location = Location.objects.create(name='DEPOT')
        form = SubLocationForm(data={'location': location.pk, 'name': 'rack 1'})
        self.assertTrue(form.is_valid())
        self.assertEqual(str(form.save()), 'DEPOT / RACK 1')

    def test_sub_location_requires_location(self):
        self.assertFalse(SubLocationForm(data={'name': 'x'}).is_valid())
