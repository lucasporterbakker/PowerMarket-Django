from django.views.generic import CreateView, TemplateView
from django.core.urlresolvers import reverse_lazy

from .forms import SupplierContactForm


class SupplierInfoView(CreateView):
    template_name = 'supplier/supplier_info.html'
    success_url = reverse_lazy('supplier:supplier_contact_success')
    form_class = SupplierContactForm


class SupplierContactSuccessView(TemplateView):
    template_name = 'supplier/supplier_contact_success.html'
