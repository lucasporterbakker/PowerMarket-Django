from django.contrib import admin

from .models import *


@admin.register(PostalCode)
class PostalCodeAdmin(admin.ModelAdmin):
    list_display = (
        'code',
        'num_locations',
    )
    search_fields = (
        'code',
    )

    def num_locations(self, obj):
        return obj.locations.count()
    num_locations.short_description = '# locations'


@admin.register(Country)
class CountryAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'num_locations',
    )
    search_fields = (
        'name',
    )

    def num_locations(self, obj):
        return obj.locations.count()
    num_locations.short_description = '# locations'


@admin.register(Location)
class LocationAdmin(admin.ModelAdmin):
    list_display = (
        'address',
        'postal_code',
        'country',
        'coords',
        'has_assessment',
        'uuid',
    )
    list_filter = (
        'country',
    )
    search_fields = (
        'address',
        'postal_code__code',
        'country__name',
    )

    def has_assessment(self, obj):
        return obj.assessments.count() > 0
    has_assessment.boolean = True
