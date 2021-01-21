from django.conf.urls import url

from .views import *


urlpatterns = [
    url(r'^information/$', SupplierInfoView.as_view(), name='supplier_info'),
    url(r'^thank-you/$', SupplierContactSuccessView.as_view(), name='supplier_contact_success')
]
