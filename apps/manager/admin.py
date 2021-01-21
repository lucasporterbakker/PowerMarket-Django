from django.contrib import admin
from django.utils.safestring import mark_safe
from django.utils.translation import ugettext_lazy as _
from django.core.urlresolvers import reverse

from apps.solar.admin import AssessmentInline
from .models import *


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'project_id',
        'profile',
        'name',
        'country',
        'selected_assessment_link',
        'created',
        'modified',
        'status',
        'stage',
    )
    list_editable = (
        'status',
        'stage',
    )
    list_filter = (
        'status',
        'stage',
        ('created', admin.DateFieldListFilter),
        ('modified', admin.DateFieldListFilter),
    )
    search_fields = (
        'profile__first_name',
        'profile__last_name',
        'profile__company',
        'profile__phone',
        'profile__user__email',
        'name',
    )

    fieldsets = (
        ('Info', {
            'fields': (
                'profile',
                'created',
                'modified',
                'name',
            )
        }),
        ('Data', {
            'fields': (
                'avg_monthly_consumption',
                'avg_monthly_bill',
                'currency',
            )
        }),
    )
    readonly_fields = ('created', 'modified', 'currency')
    inlines = [AssessmentInline]

    def selected_assessment_link(self, obj):
        if obj.selected_assessment:
            link = '<a href="{}" target="_blank">{}</a>'.format(
                reverse('admin:solar_assessment_change', args=(obj.selected_assessment.id,)),
                obj.selected_assessment.uuid
            )
            return mark_safe(link)
    selected_assessment_link.short_description = _('assessment')

    def currency(self, obj):
        try:
            return obj.selected_assessment.get_currency_display()
        except:
            pass
    currency.short_description = _('currency')


class ProjectInline(admin.TabularInline):
    model = Project
    fields = ('name',)
    show_change_link = True
    extra = 1


@admin.register(Offer)
class OfferAdmin(admin.ModelAdmin):
    list_display = ('created', 'modified', 'supplier', 'project', 'status')
    list_editable = ('supplier', 'project', 'status',)


@admin.register(ElectricityBill)
class ElectricityBillAdmin(admin.ModelAdmin):
    list_display = ('created', 'profile', 'project', 'date', 'private_file')
    list_filter = (
        ('created', admin.DateFieldListFilter),
        ('modified', admin.DateFieldListFilter),
    )

    def profile(self, obj):
        try:
            return obj.project.profile
        except:
            pass
    profile.short_description = _('profile')
