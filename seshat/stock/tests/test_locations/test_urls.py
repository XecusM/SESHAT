from django.test import SimpleTestCase
from django.urls import reverse, resolve

from stock.views import locations as views


class LocationUrlsTest(SimpleTestCase):
    '''
    Test the location urls
    '''

    def test_urls(self):
        cases = [
            ('stock:NewLocation', views.NewLocation, None),
            ('stock:EditLocation', views.EditLocation, {'pk': 1}),
            ('stock:LocationsList', views.LocationsList, None),
            ('stock:LocationDetails', views.LocationDetails, {'pk': 1}),
            ('stock:DeleteLocation', views.delete_location, {'pk': 1}),
            ('stock:NewSubLocation', views.NewSubLocation, None),
            ('stock:EditSubLocation', views.EditSubLocation, {'pk': 1}),
            ('stock:SubLocationsList', views.SubLocationsList, None),
            ('stock:SubLocationDetails', views.SubLocationDetails, {'pk': 1}),
            ('stock:DeleteSubLocation', views.delete_sublocation, {'pk': 1}),
        ]
        for name, view, kwargs in cases:
            match = resolve(reverse(name, kwargs=kwargs))
            self.assertEqual(getattr(match.func, 'view_class', match.func), view, name)
