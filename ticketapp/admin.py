from django.contrib import admin
from .models import *
# Register your models here.
from tinymce.widgets import TinyMCE
from .forms import ImapForm


class TicketAdmin(admin.ModelAdmin):
    list_display = (
        'ticket_id',
        'title',
        'customer_full_name',
        'customer_phone_number',
        'customer_email',
        'ticket_section',
        'ticket_priority',
        'completed_status',
        'assigned_to',
        'resolved_by'
    )
    formfield_overrides = {
        models.TextField: {'widget': TinyMCE()}
    }
    list_filter = (
        # 'ticket_section',
        'ticket_priority',
        'title',
        'completed_status',
    )

    search_fields = ('title',)


class OutgoinEmailSettingsAdmin(admin.ModelAdmin):
    formfield_overrides = {
        models.TextField: {'widget': TinyMCE()}
    }


class ImapAdmin(admin.ModelAdmin):
    form = ImapForm


admin.site.register(Ticket, TicketAdmin)
admin.site.register(OutgoinEmailSettings, OutgoinEmailSettingsAdmin)
admin.site.register(ImapSettings, ImapAdmin)
admin.site.register(Comment)
admin.site.register([MediaFiles, ])
