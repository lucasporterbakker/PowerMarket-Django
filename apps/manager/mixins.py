from django.http import HttpResponseForbidden


class ProjectEditPermissionMixin(object):
    """
    Checks whether user has object-level edit permissions for the project.
    Permissions are defined in the project model.
    Use on AJAX modal views.
    """
    def dispatch(self, *args, **kwargs):
        # TODO: improve this..
        project = self.get_object()
        if not project.has_object_edit_permission(self.request):
            return HttpResponseForbidden()
        else:
            return super(ProjectEditPermissionMixin, self).dispatch(*args, **kwargs)