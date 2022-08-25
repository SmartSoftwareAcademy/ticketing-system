from datetime import datetime
from apscheduler.schedulers.background import BackgroundScheduler
#from .import_email_tickets import import_email
from ticketapp.get_email import EmailDownload
#from django.core.mail.backends.smtp import EmailBackend
from ticketapp.models import *


def start(request):
    try:
        imap_settings = ImapSettings.objects.all()[0]
        scheduler = BackgroundScheduler()
        scheduler.add_job(EmailDownload(request, imap_settings.email_id,
                                        imap_settings.email_password).login_to_imap_server, 'interval', minutes=0.25)
        scheduler.start()
    except Exception as e:
        print(e)
