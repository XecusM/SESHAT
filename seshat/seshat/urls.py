"""seshat URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.conf.urls.static import static
from django.views.static import serve
from django.conf import settings
from django.conf.urls.i18n import i18n_patterns

from . import views


urlpatterns = [
    # multi langauge application
    path('i18n/', include('django.conf.urls.i18n')),
]

urlpatterns += i18n_patterns(
    # Index page
    path('', views.Index.as_view(), name='index'),
    # backup page
    path('backup/', views.databackup, name='backup'),
    # download backup file
    path(
        'backup/download/<int:pk>',
        views.databackup_download,
        name='download_backup'),
    # restore page
    path('restore/', views.datarestore, name='restore'),
    # export page
    path('export/', views.dataexport, name='export'),
    # import page
    path('import/', views.dataimport, name='import'),
    # download import template file
    path(
        'import/download/<int:pk>',
        views.dataimport_template,
        name='download_template'),
    # account application for user accounts
    path('accounts/', include('account.urls')),
    # customer application for customers details
    path('customers/', include('customer.urls')),
    # purchase application for purchases details
    path('purchases/', include('purchase.urls')),
    # sell application for sells details
    path('sales/', include('sale.urls')),
    # stock application for stocks details
    path('stock/', include('stock.urls')),
    # vendor application for vendors details
    path('vendors/', include('vendor.urls')),
    # remove prefix for the default language
    prefix_default_language=False,
)

# media settings
if settings.DEBUG:
    urlpatterns += static(
                        settings.STATIC_URL,
                        serve,
                        document_root=settings.STATIC_ROOT
    )
    urlpatterns += static(
                        settings.MEDIA_URL,
                        serve,
                        document_root=settings.MEDIA_ROOT
    )


# error handlers
handler400 = views.error_400
handler403 = views.error_403
handler404 = views.error_404
handler500 = views.error_500
