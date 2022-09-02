from pytz import timezone
from django.apps import AppConfig
from django.conf import settings


class TicketappConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'ticketapp'

    def ready(request):
        from ticketsupdater import updater
        from .models import ImapSettings, TicketSettings
        from .views import load_time_zone

        imap_settings = ImapSettings.objects.all().first()

        load_time_zone()
        if settings.SCHEDULER_AUTOSTART:
            updater.start(request)
            updater.escallate(request)
