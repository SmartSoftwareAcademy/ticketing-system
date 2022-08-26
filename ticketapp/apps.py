from pytz import timezone
from django.apps import AppConfig


class TicketappConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'ticketapp'

    def ready(request):
        from ticketsupdater import updater
        from .models import ImapSettings, TicketSettings
        from .views import load_time_zone

        imap_settings = ImapSettings.objects.all().first()
        ticket_settings = TicketSettings.objects.all().first()

        load_time_zone()

        if imap_settings.auto_import_mails_as_tickets:
            updater.start(request)

        if ticket_settings.enable_ticket_escalltion:
            updater.escallate(request)
