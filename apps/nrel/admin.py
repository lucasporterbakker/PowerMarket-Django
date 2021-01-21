from django.contrib.gis import admin

from import_export.admin import ImportExportModelAdmin

from .models import *


@admin.register(NoDataError)
class AssessmentAdmin(ImportExportModelAdmin):
    list_display = (
        'created',
        'lat',
        'lon',
    )
