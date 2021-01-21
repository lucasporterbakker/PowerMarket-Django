from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User
from django.template.loader import render_to_string
from django.utils.translation import ugettext_lazy as _


admin.site.unregister(User)


# JS links relative to static.
# bootstrap_css = "bower_components/bootstrap/dist/js/bootstrap.js",

# JS links relative to static.
jquery_js = "bower_components/jquery/dist/jquery.js"
bootstrap_js = "bower_components/bootstrap/dist/js/bootstrap.js"
modal_js = "js/modal.js"


def inline_link_button(url, label=None, css_class=None, extra_styles=None):
    template = "admin/elements/inline_link_button.html"
    return render_to_string(
        template,
        context={
            "url": url,
            "label": label,
            "css_class": css_class,
            "extra_styles": extra_styles,
        }
    )


@admin.register(User)
class UserAdmin(UserAdmin):
    list_display = (
        'username',
        'email',
        'group_list',
        'date_joined',
        'is_active',
        'is_staff',
        'is_superuser',
    )

    def group_list(self, obj):
        return ", ".join([group.name for group in obj.groups.all()])
    group_list.short_description = _('groups')
