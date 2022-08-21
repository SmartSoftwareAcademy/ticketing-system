from django.apps import AppConfig


class TicketappConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'ticketapp'

    def ready(request):
        from ticketsupdater import updater
        from .models import ImapSettings
        imap_settings = ImapSettings.objects.all().first()
        if imap_settings.auto_import_mails_as_tickets:
            updater.start(request)
        else:
            pass
