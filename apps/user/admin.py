from django.contrib import admin
from django.core.urlresolvers import reverse
from django.utils import timezone
from django.utils.safestring import mark_safe
from django.utils.translation import ugettext_lazy as _

from liststyle.admin import ListStyleAdminMixin

from powermarket.admin import (
    bootstrap_js,
    inline_link_button,
    jquery_js,
    modal_js,
)
from apps.manager.admin import ProjectInline
from .models import (
    UserProfile,
    StaffProfile,
    Contact,
    ContactNote,
)


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = (
        'created',
        'user',
        'first_name',
        'last_name',
        'company',
        'phone',
        'get_selected_project',
        'get_project_status',
        'get_linkedin_link',
        'test',
        'qualified_lead',
        'impersonate',
    )
    list_editable = (
        'test',
        'qualified_lead',
    )
    list_filter = (
        'test',
        'qualified_lead',
    )
    search_fields = (
        'user',
        'company',
        'phone',
    )
    fieldsets = (
        (None, {
            'fields': (
                'user',
                'company',
                'phone',
                'linkedin_url',
                'test',
                'qualified_lead',
                'created',
                'modified',
            )
        }),
    )
    readonly_fields = (
        'linkedin_url',
        'created',
        'modified',
    )
    inlines = [ProjectInline]

    def get_selected_project(self, obj):
        project = obj.selected_project
        if project:
            return mark_safe(
                "<a href='{}' target='_blank'>{}</a>".format(
                    reverse('admin:manager_project_change', args=[project.id]),
                    project,
                )
            )
    get_selected_project.short_description = _('selected project')

    def get_project_status(self, obj):
        project = obj.selected_project
        if project:
            return project.get_status_display()
    get_project_status.short_description = _('project status')

    def get_linkedin_link(self, obj):
        if obj.linkedin_url:
            return mark_safe(
                "<a href='{}' target='_blank'>{}</a>".format(
                    obj.linkedin_url,
                    obj.linkedin_url,
                )
            )
    get_linkedin_link.short_description = _('LinkedIn link')

    def impersonate(self, obj):
        url = reverse(
            'impersonate-start',
            kwargs={'uid': obj.user.id},
        )
        return inline_link_button(
            url,
            label=_('Show profile'),
        )
    impersonate.short_description = _('Impersonate')
    impersonate.allow_tags = True


@admin.register(StaffProfile)
class StaffProfileAdmin(admin.ModelAdmin):
    list_display = (
        'user',
    )


class ContactNoteTabInline(admin.TabularInline):
    model = ContactNote
    extra = 0

    fields = (
        'note',
        'created',
        'created_by',
        'modified',
        'modified_by',
    )
    readonly_fields = (
        'created',
        'created_by',
        'modified',
        'modified_by',
    )


class ContactTabInline(admin.TabularInline):
    model = Contact
    extra = 0


@admin.register(Contact)
class ContactAdmin(
    admin.ModelAdmin,
    ListStyleAdminMixin,
):
    list_display = (
        'created',
        'name',
        'company',
        'email',
        'phone',
        'test',
        'fake',
        'qualified_lead',
        'status_modified',
        'status',
        # 'display_notes',
        'report_link',
    )
    list_editable = (
        'test',
        'fake',
        'qualified_lead',
        'status',
    )
    list_filter = (
        'test',
        'fake',
        'qualified_lead',
        'status',
    )
    search_fields = (
        'name',
        'company',
        'email',
        'phone',
    )

    inlines = [
        ContactNoteTabInline,
    ]

    class Media:
        js = (
            jquery_js,
            bootstrap_js,
            modal_js,
        )

    def save_model(self, request, obj, form, change):
        db_instance = Contact.objects.filter(pk=obj.pk).first()
        if db_instance:
            if db_instance.status != obj.status:
                obj.status_modified_on = timezone.now()
                obj.status_modified_by = request.user
        super(ContactAdmin, self).save_model(request, obj, form, change)

    def status_modified(self, obj):
        if obj.status_modified_on:
            status_modified = "{}".format(
                obj.status_modified_on.strftime("%Y-%m-%d %H:%Mh"),
            )
            if obj.status_modified_by:
                status_modified += "<br/>by <a href='{}' class='admin-inline-link'>{}</a>".format(
                    reverse('admin:auth_user_change', args=(obj.status_modified_by.id,)),
                    obj.status_modified_by,
                )
            return mark_safe(status_modified)

    def display_notes(self, obj):
        notes_html = "".join(
            "<b>{}:</b><br/>{}<br/>".format(note.created.strftime("%Y-%m-%d %H:%Mh"), note.note)
            for note in obj.notes.all()
        )
        create_note_url = "javascript:createModal('" + reverse('user:contact_note_create') + "');"
        notes_html += inline_link_button(
            create_note_url,
            label=_("Add note"),
            css_class="btn-primary btn-xs vpad-5",
        )
        return mark_safe(notes_html)
    display_notes.short_description = _('notes')

    def report_link(self, obj):
        assessment = obj.assessments.first()
        if assessment:
            report_link_html = (
                "<a href='{report_link}' target='_blank' class='admin-inline-link'>{report_link}</a>".format(
                report_link=assessment.short_link,
                )
            )
            return mark_safe(report_link_html)
    report_link.short_description = _('report link')

    def get_row_css(self, obj, index):
        status = obj.status
        if obj.test:
            list_style = 'list-style-lightest-gray'
        elif status in [
            obj.STATUS_CONTACTED,
            obj.STATUS_PROCESSING,
        ]:
            list_style = 'list-style-warning'
        elif status in [
            obj.STATUS_OFFER_DELIVERED,
        ]:
            list_style = 'list-style-info'
        elif status in [
            obj.STATUS_SALE_COMPLETE,
        ]:
            list_style = 'list-style-success'
        elif status in [
            obj.STATUS_NO_RESPONSE,
            obj.STATUS_NOT_INTERESTED,
        ]:
            list_style = 'list-style-danger'
        else:
            list_style = 'list-style-white'
        return list_style
