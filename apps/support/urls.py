from django.conf.urls import url

from .views import *


urlpatterns = [
    url(r'^$', SupportPageView.as_view(), name='support'),
    url(r'^call-request-success/$', CallRequestSuccessView.as_view(), name='call_request_success')
]
