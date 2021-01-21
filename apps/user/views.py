from django.views.generic import (
    CreateView,
    DeleteView,
    TemplateView,
    UpdateView,
)
from django.utils.translation import ugettext_lazy as _
from django.core.urlresolvers import reverse
from django.http import JsonResponse

from powermarket.mixins import ModalResponseMixin
from .forms import *
from .mixins import ProfileEditPermissionMixin


class ProfileView(TemplateView):
    template_name = 'user/profile.html'


class PersonalInformationUpdateView(
    ModalResponseMixin,
    ProfileEditPermissionMixin,
    UpdateView,
):
    model = UserProfile
    form_class = PersonalInformationForm
    modal_title = _('Personal Information')

    def form_valid(self, form):
        response = super(PersonalInformationUpdateView, self).form_valid(form)
        self.object.selected_project.update_stage()
        return response


class DeleteAccountView(ModalResponseMixin, ProfileEditPermissionMixin, DeleteView):
    model = UserProfile
    modal_title = _("Delete account")
    modal_content = _("Are you sure that you want to delete your account? "
                      "All your data will be lost.")
    form_submit_label = _('Yes, delete!')

    def delete(self, request, *args, **kwargs):
        """
        Calls the delete() method on the fetched object and then
        redirects to the success URL.
        """
        profile = self.get_object()
        success_url = self.get_success_url()
        profile.user.delete()
        return JsonResponse({
            'html': None,
            'valid': True,
            'success_url': str(success_url)  # str() conversion is necessary for reverse_lazy.
        })

    def get_success_url(self):
        return reverse('landing_page')


#    Admin views.
# ---------------------------

class ContactNoteCreateView(ModalResponseMixin, CreateView):
    model = ContactNote
    fields = (
        'note',
    )

