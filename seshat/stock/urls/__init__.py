from django.urls import path

from . import categories, locations, items, moves
from ..views import items as item_views

# application name
app_name = 'stock'

# patterns
urlpatterns = [
    # stock dashboard
    path('', item_views.Index.as_view(), name='Index'),
]
urlpatterns += categories.urlpatterns
urlpatterns += locations.urlpatterns
urlpatterns += items.urlpatterns
urlpatterns += moves.urlpatterns
