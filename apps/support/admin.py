from django.contrib import admin
from django.utils.translation import ugettext_lazy as _

from .models import SupportTicket, SupportAction, CallRequest


@admin.register(SupportAction)
class SupportActionAdmin(admin.ModelAdmin):
    list_display = ('name', 'description')
    search_fields = ('name', 'description')


@admin.register(SupportTicket)
class SupportTicketAdmin(admin.ModelAdmin):
    list_display = ('id', 'status', 'contact', 'assignee', 'get_required_actions_list', 'automatic')
    list_editable = ('status',)
    list_filter = ('status', 'automatic')
    search_fields = ('contact', 'assignee')

    def get_required_actions_list(self, obj):
        return obj.get_required_actions_list()
    get_required_actions_list.short_description = _('required actions')


@admin.register(CallRequest)
class CallRequestAdmin(admin.ModelAdmin):
    list_display = ('name', 'phone', 'note', 'contacted')
    search_fields = ('name', 'phone')

