from django.conf.urls import url
from django.contrib.auth.decorators import login_required

from . import views


urlpatterns = [

    # AJAX views.
    url(r'^offer-review/(?P<pk>[0-9]+)$', views.OfferReviewView.as_view(), name='offer_review'),
    url(r'^electricity-bill/create/$', views.ElectricityBillModalCreateView.as_view(), name='create_electricity_bill'),
    url(r'^electricity-bill/(?P<pk>[0-9]+)/delete/$', views.delete_electricity_bill_view, name='delete_electricity_bill'),
    url(r'^project/(?P<pk>[0-9]+)/pause/$', login_required(views.pause_project_view), name='pause_project'),
    url(r'^project/(?P<pk>[0-9]+)/resume/$', login_required(views.resume_project_view), name='resume_project'),
    url(r'^dashboard/$', login_required(views.DashboardView.as_view()), name='dashboard'),
]

'''
url(r'^electricity-bill/create/$', views.ElectricityBillCreateView.as_view(),
    name='electricity_bill_create'),
url(r'^electricity-bill/update/(?P<pk>[0-9]+)/$', views.ElectricityBillUpdateView.as_view(),
    name='electricity_bill_update'),
'''
