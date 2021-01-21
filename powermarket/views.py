from django.shortcuts import render_to_response
from django.template import RequestContext
from django.views.generic import TemplateView
from django.conf import settings
from django.http import Http404
from django.utils.translation import ugettext_lazy as _

from apps.user.models import Contact
from apps.solar.models import Assessment
from .mixins import ModalResponseMixin


# Error views.
# -----------------------------------------------------------------------------

def custom400view(request):
    response = render_to_response('400.html', {}, context_instance=RequestContext(request))
    response.status_code = 400
    return response


def custom403view(request):
    response = render_to_response('403.html', {}, context_instance=RequestContext(request))
    response.status_code = 403
    return response


def custom404view(request):
    response = render_to_response('404.html', {}, context_instance=RequestContext(request))
    response.status_code = 404
    return response


def custom500view(request):
    response = render_to_response('500.html', {}, context_instance=RequestContext(request))
    response.status_code = 500
    return response


class OopsView(TemplateView):
    template_name = 'oops.html'


# Maintenance views.
# -----------------------------------------------------------------------------

class ComingSoonModalView(ModalResponseMixin, TemplateView):
    modal_title = _('Coming soon!')
    modal_content = _('This feature is not quite ready yet, but will be available soon.')
    form_cancel_label = _('Ok, close')
    form_submit_label = None


# Test views.
# -----------------------------------------------------------------------------

class EmailTestView(TemplateView):
    template_name = 'email/test_email.html'

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_staff:
            raise Http404()
        else:
            return super(EmailTestView, self).dispatch(request, *args, **kwargs)

    def get_template_names(self):
        template_kwarg = self.kwargs.get('template_name')
        if template_kwarg:
            return template_kwarg.replace('__', '/') + '.html'
        else:
            return self.template_name

    def get_context_data(self, **kwargs):
        context = super(EmailTestView, self).get_context_data(**kwargs)
        context.update({
            'subject': 'Test Email',
            'contact': Contact.objects.first(),
            'assessment': Assessment.objects.first(),
        })
        return context
