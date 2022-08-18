from django.apps import AppConfig


class TicketappConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'ticketapp'

    def ready(self):
        # from ticketsupdater import updater
        # updater.start()
        pass
