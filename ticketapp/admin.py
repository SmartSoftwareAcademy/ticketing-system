from django.contrib import admin
from .models import *
# Register your models here.
from tinymce.widgets import TinyMCE
from .forms import ImapForm


class TicketAdmin(admin.ModelAdmin):
    list_per_page=10
    list_display = [
        'ticket_id',
        'title',
        'customer_full_name',
        'customer_phone_number',
        'customer_email',
        'ticket_section',
        'ticket_priority',
        'ticket_status',
        'assigned_to',
        'resolved_by',
        'created_date',
        'resolved_date',
    ]
    formfield_overrides = {
        models.TextField: {'widget': TinyMCE()}
    }
    list_filter = (
        'ticket_section',
        'ticket_priority',
        'ticket_status',
        'resolved_by',
        'tags__tag_name',
        'created_date',
        'resolved_date',
        'assigned_to',
    )

    search_fields = ('title', 'ticket_status', 'ticket_id' 'created_date','resolved_date','assigned_to','resolved_by')
    list_display_links=['ticket_id']
    list_editable=['ticket_status','created_date','resolved_date','assigned_to','resolved_by']


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


class TicketSettingAdmin(admin.ModelAdmin):
    formfield_overrides = {
        models.TextField: {'widget': TinyMCE()}
    }
    list_filter = (
        'id',
        'duration_before_escallation',
        'duration_before_escallation',
    )

    search_fields = ('id', 'duration_before_escallation',
                     'duration_before_escallation',)


class ImapAdmin(admin.ModelAdmin):
    form = ImapForm

admin.site.register(System_Settings)
admin.site.register(Ticket, TicketAdmin)
admin.site.register(OutgoinEmailSettings, OutgoinEmailSettingsAdmin)
admin.site.register(ImapSettings, ImapAdmin)
admin.site.register(Comment, CommentAdmin)
admin.site.register(TicketSettings, TicketSettingAdmin)

admin.site.register([MediaFiles, Tags])
