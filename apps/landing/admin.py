from django import forms
from django.contrib import admin

from ckeditor.widgets import CKEditorWidget
from import_export import resources
from import_export.admin import ImportExportModelAdmin

from .models import *


class GlossaryEntryResource(resources.ModelResource):
    class Meta:
        model = LexiconEntry


class LexiconAdminForm(forms.ModelForm):
    class Meta:
        model = LexiconEntry
        fields = '__all__'
        widgets = {
            'description': CKEditorWidget(),
        }


@admin.register(LexiconEntry)
class LexiconEntryAdmin(ImportExportModelAdmin):
    form = LexiconAdminForm
    prepopulated_fields = {"slug": ("term",)}
    list_display = (
        'term',
        'slug',
        'abbreviation',
        'status',
        'published',
    )
    list_editable = (
        'status',
    )
    list_filter = (
        'status',
        'published',
    )
    search_fields = (
        'term',
        'abbreviation',
    )


class PressEntryResource(resources.ModelResource):
    class Meta:
        model = PressEntry


class PressEntryAdminForm(forms.ModelForm):
    class Meta:
        Model = PressEntry
        fields = '__all__'
        widgets = {
            # 'details': CKEditorWidget(),
        }


@admin.register(PressEntry)
class PressEntryAdmin(ImportExportModelAdmin):
    form = PressEntryAdminForm
    list_display = (
        'date',
        'title',
        'headline',
        'link',
    )
    search_fields = (
        'title',
        'headline',
        'details',
    )
