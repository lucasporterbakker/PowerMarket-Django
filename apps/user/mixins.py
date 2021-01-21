from django.http import HttpResponseForbidden


class ProfileEditPermissionMixin(object):
    """
    Checks whether user has object-level edit permissions for the profile.
    Permissions are defined in the profile
     model.
    Use on AJAX modal views.
    """
    def dispatch(self, *args, **kwargs):
        # TODO: improve this..
        profile = self.get_object()
        if not profile.has_object_edit_permission(self.request):
            return HttpResponseForbidden()
        else:
            return super(ProfileEditPermissionMixin, self).dispatch(*args, **kwargs)