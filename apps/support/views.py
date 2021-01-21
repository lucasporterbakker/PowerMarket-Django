from django.views.generic import CreateView, TemplateView
from django.core.urlresolvers import reverse_lazy

from .forms import CallRequestForm


class SupportPageView(CreateView):
    template_name = 'support/support.html'
    success_url = reverse_lazy('support:call_request_success')
    form_class = CallRequestForm


class CallRequestSuccessView(TemplateView):
    template_name = 'support/call_request_success.html'
