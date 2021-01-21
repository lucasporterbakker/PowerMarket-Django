from django import forms
from django.contrib.gis import admin
from django.core.urlresolvers import reverse
from django.utils.safestring import mark_safe
from django.utils.translation import ugettext_lazy as _

from ckeditor.widgets import CKEditorWidget
from import_export.admin import ImportExportModelAdmin

from .models import (
    Assessment,
    ExampleAssessment,
)


class AssessmentInline(admin.TabularInline):
    model = Assessment
    extra = 0


@admin.register(Assessment)
class AssessmentAdmin(ImportExportModelAdmin):
    list_display = (
        'created',
        'short_link',
        'country',
        'postal_code',
        'currency',
        'contact',
        'project_link',
        'selected_area',
        'system_capacity_estimate',
        'annual_energy_estimate',
        'type',
        'is_example',
        'test',
        'supervised',
        'useless',
        'duplicate',
        'nrel_station_distance',
    )
    list_editable = (
        'type',
        'test',
        'supervised',
        'useless',
        'duplicate',
    )
    list_filter = (
        'type',
        'useless',
        'test',
        'duplicate',
    )
    search_fields = (
        'uuid',
        'contact__email',
    )

    fieldsets = (
        (None, {
            'fields': (
                'created',
                'uuid',
                'project',
                'contact',
                'email_sent',
                'type',
            ),
        }),
        ('Flags', {
            'fields': (
                'test',
                'supervised',
                'useless',
            ),
        }),
        ('Location', {
            'fields': (
                'location',
            ),
        }),
        ('Selected area', {
            'fields': (
                'mpoly',
                'mpoly_str',
                'num_points',
                'selected_area',
            ),
        }),
        ('System', {
            'fields': (
                'system_capacity_estimate',
            )
        }),
        ('Energy', {
            'fields': (
                'monthly_energy_estimates',
                'annual_energy_estimate',
            ),
        }),
        ('Profit', {
            'fields': (
                'monthly_savings_estimates',
                'annual_savings_estimate',
                'monthly_earnings_estimates',
                'annual_earnings_estimate',
            ),
        }),
        ('NREL info', {
            'fields': (
                'nrel_version',
                'nrel_station_distance',
            )
        })
    )

    readonly_fields = (
        'uuid',
        'created',
        'num_points',
        'mpoly_str',
        'location',
        'selected_area',
        'system_capacity_estimate',
        'monthly_energy_estimates',
        'annual_energy_estimate',
        'monthly_savings_estimates',
        'annual_savings_estimate',
        'monthly_earnings_estimates',
        'annual_earnings_estimate',
    )

    def mpoly_str(self, obj):
        return "{}".format(obj.mpoly)
    mpoly_str.short_description = _('mpoly')

    def annual_profit_estimate(self, obj):
        return obj.annual_profit_estimate
    annual_profit_estimate.short_description = _('Annual profit estimate [£]')

    def short_link(self, obj):
        link = obj.short_link
        return mark_safe('<a href="{}">{}</a>'.format(link, link))
    short_link.short_description = 'short link'
    short_link.allow_tags = True

    def project_link(self, obj):
        project = obj.project
        if project:
            url = reverse('admin:manager_project_change', args=(project.id,))
            return '<a href="%s">%s</a>' % (url, project)
    project_link.allow_tags = True

    def is_example(self, obj):
        return obj.is_example
    is_example.boolean = True


class ExampleAssessmentAdminForm(forms.ModelForm):
    class Meta:
        Model = ExampleAssessment
        fields = '__all__'
        widgets = {
            'info': CKEditorWidget(),
        }


@admin.register(ExampleAssessment)
class ExampleAssessmentAdmin(admin.ModelAdmin):
    form = ExampleAssessmentAdminForm
    list_display = (
        'name',
        'address',
        'assessment',
        'published',
    )
    list_filter = (
        'published',
    )
    search_fields = (
        'name',
        'assessment__uuid',
    )
    prepopulated_fields = {'slug': ('name',)}
