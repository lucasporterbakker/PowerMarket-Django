from django.contrib import admin

from .models import (
    SupplierContact,
    SupplierProfile,
)


@admin.register(SupplierContact)
class SupplierContactAdmin(admin.ModelAdmin):
    list_display = (
        'created',
        'company',
        'email',
        'phone',
        'website',
        'type_of_business',
    )


@admin.register(SupplierProfile)
class SupplierProfileAdmin(admin.ModelAdmin):
    list_display = (
        'user',
        'name',
        'contact_person',
        'phone',
    )
