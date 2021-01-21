from django.http import JsonResponse
from django.utils.translation import ugettext_lazy as _
from django.template import RequestContext
from django.template.loader import render_to_string


class ModalResponseMixin(object):
    template_name = 'modal.html'
    success_url = None
    modal_title = None
    modal_content = None
    form_submit_label = _('Update')
    form_cancel_label = _('Cancel')
    object = None

    def get_modal_title(self):
        return self.modal_title

    def get_modal_content(self):
        return self.modal_content

    def get_form_action_url(self):
        if hasattr(self, 'form_action_url'):
            return self.form_action_url

    def get_form_info(self):
        if hasattr(self, 'form_info'):
            return self.form_info

    def get_additional_context(self):
        return {}

    def form_invalid(self, form):
        response = super(ModalResponseMixin, self).form_invalid(form)
        if self.request.is_ajax():
            return self.render_to_response(form, valid=False)
        else:
            return response

    def form_valid(self, form):
        response = super(ModalResponseMixin, self).form_valid(form)
        if self.request.is_ajax():
            return self.render_to_response(form, valid=True)
        else:
            return response

    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()
        success_url = self.get_success_url()
        self.object.delete()
        return JsonResponse(
            {
                'html': None,
                'valid': True,
                'success_url': str(success_url)
            }
        )

    def get_success_url(self):
        if self.success_url:
            return self.success_url
        elif self.request.is_ajax():
            return '#'

    def render_to_response(self, context, **kwargs):
        if self.request.is_ajax():
            if kwargs.get('form'):
                form = kwargs['form']
            else:
                try:
                    form = self.get_form()
                except:
                    form = None
                    pass
            if kwargs.get('valid'):
                valid = kwargs['valid']
            else:
                valid = False
            ctx = {
                'object': self.object,
                'form': form,
                'modal_title': self.get_modal_title(),
                'modal_content': self.modal_content,
                'form_action_url': self.get_form_action_url(),
                'form_info': self.get_form_info(),
                'form_submit_label': self.form_submit_label,
                'form_cancel_label': self.form_cancel_label,
            }
            ctx.update()
            context_instance = RequestContext(self.request)
            html_rendered = render_to_string(self.template_name, ctx, context_instance=context_instance)
            return JsonResponse(
                {
                    'html': html_rendered,
                    'valid': valid,
                    'success_url': str(self.get_success_url())
                }
            )
        else:
            return super(ModalResponseMixin, self).render_to_response(context, **kwargs)
