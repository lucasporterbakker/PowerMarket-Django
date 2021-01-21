from django.conf.urls import include, url
from django.conf.urls.static import static
from django.core.urlresolvers import reverse_lazy
from django.contrib import admin
from django.contrib.sitemaps.views import sitemap
from django.views.generic import TemplateView

import private_storage.urls
from rest_framework.routers import DefaultRouter

from powermarket.views import OopsView
from apps.landing.views import LandingPageView
from apps.solar.views import report_link_view
from apps.solar import api as solar_api
from .sitemaps import *
from .views import *


admin.autodiscover()

handler400 = OopsView.as_view()
handler403 = OopsView.as_view()
handler404 = OopsView.as_view()
handler500 = OopsView.as_view()

sitemaps = {
    'static_pages': StaticPagesSitemap,
    'blog_pages': BlogPagesSitemap,
    'dynamic_pages': DynamicPagesSitemap,
    'allauth': AllauthSitemap,
    'supplier_app': SupplierAppSitemap,
    'solar_app': SolarAppSitemap,
    'support_app': SupportAppSitemap,
}

router = DefaultRouter()
router.register(r'solar-potential/assessment', solar_api.AssessmentViewSet)

api_urlpatterns = router.urls
api_urlpatterns += [
    url(r'^solar/environmental-benefits/?(?P<energy>[a-zA-Z0-9_.-]*)/$',
        solar_api.EnvironmentalBenefitsAPIView.as_view(),
        name='environmental_benefits',
        ),
    url(r'^solar/fit-rate/(?P<annual_energy>[0-9.]*)/(?P<target_date>[0-9-]*)$',
        solar_api.FitRateAPIView.as_view(),
        name='fit_rate',
        )
]

urlpatterns = [

    url(r'^admin/', include(admin.site.urls)),
    url(r'^ckeditor/', include('ckeditor_uploader.urls')),
    url(r'^impersonate/', include('impersonate.urls')),
    url(r'^accounts/', include('allauth.urls')),
    url(r'^hello/$', LandingPageView.as_view(), name='hello'),
    url(r'^', include('apps.landing.urls')),
    url(r'^', include('apps.manager.urls', namespace='manager')),
    url(r'^user/', include('apps.user.urls', namespace='user')),
    url(r'^support/', include('apps.support.urls', namespace='support')),
    url(r'^supplier/', include('apps.supplier.urls', namespace='supplier')),
    url(r'^solar/', include('apps.solar.urls', namespace='solar')),
    url(r'^r/(?P<uuid>[a-zA-Z0-9_.-]*)/$', report_link_view, name='report_link'),
    url(r'^api/', include(api_urlpatterns, namespace='api')),
    url(r'^api-auth/', include('rest_framework.urls', namespace='rest_framework')),
    url('^private/', include(private_storage.urls)),
    url(r'^sitemap\.xml$', sitemap, {'sitemaps': sitemaps}, name='django.contrib.sitemaps.views.sitemap'),
    url(r'^robots\.txt$', TemplateView.as_view(template_name='robots.txt', content_type='text/plain')),
    url(r'^email-test/$', EmailTestView.as_view()),
    url(r'^email-test/(?P<template_name>[\w-]+)/?$', EmailTestView.as_view()),
    url(r'^coming-soon/$', ComingSoonModalView.as_view(), name='coming_soon'),
    url(r'^400/$', OopsView.as_view(), name='400'),
    url(r'^403/$', OopsView.as_view(), name='403'),
    url(r'^404/$', OopsView.as_view(), name='404'),
    url(r'^500/$', OopsView.as_view(), name='500'),
    url(r'^oops/$', OopsView.as_view(), name='oops'),
    url(r'^.*/$', OopsView.as_view())

] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
