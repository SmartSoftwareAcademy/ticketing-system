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
        'ticket_status',
        'assigned_to',
        'resolved_by'
    )
    formfield_overrides = {
        models.TextField: {'widget': TinyMCE()}
    }
    list_filter = (
        'ticket_section',
        'ticket_priority',
        'ticket_status',
        'tags__tag_name',
    )

    search_fields = ('title', 'ticket_status', 'tcket_id',)


class OutgoinEmailSettingsAdmin(admin.ModelAdmin):
    formfield_overrides = {
        models.TextField: {'widget': TinyMCE()}
    }


class CommentAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'text',
        'created_date',
    )
    formfield_overrides = {
        models.TextField: {'widget': TinyMCE()}
    }
    list_filter = (
        'user__username',
        'created_date',
    )

    search_fields = ('text', 'ticket__id', 'user__username', 'created_date',)


class ImapAdmin(admin.ModelAdmin):
    form = ImapForm


admin.site.register(Ticket, TicketAdmin)
admin.site.register(OutgoinEmailSettings, OutgoinEmailSettingsAdmin)
admin.site.register(ImapSettings, ImapAdmin)
admin.site.register(Comment, CommentAdmin)
admin.site.register([MediaFiles, Tags])
