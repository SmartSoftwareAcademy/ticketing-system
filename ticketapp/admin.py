from django.contrib import admin
from .models import *
# Register your models here.


@admin.register(Ticket)
class TicketAdmin(admin.ModelAdmin):
    list_display = (
        'ticket_id',
        'title',
        # 'customer_full_name',
        # 'customer_phone_number',
        # 'customer_email',
        # 'ticket_section',
        'ticket_priority',
        'completed_status',
        'assigned_to',
        'resolved_by'
    )
    list_filter = (
        # 'ticket_section',
        'ticket_priority',
        'title',
        'completed_status',
    )

    search_fields = ('title',)


admin.site.register(Comment)
admin.site.register(MediaFiles)
