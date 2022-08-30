from datetime import datetime
from sched import scheduler
from apscheduler.schedulers.background import BackgroundScheduler
#from .import_email_tickets import import_email
from ticketapp.get_email import EmailDownload
#from django.core.mail.backends.smtp import EmailBackend
from ticketapp.models import *
from ticketapp.views import Escallate


def start(request):
    try:
        imap_settings = ImapSettings.objects.all()[0]
        job = EmailDownload(request, imap_settings.email_id,
                            imap_settings.email_password).login_to_imap_server
        scheduler = BackgroundScheduler()
        scheduler.add_job(job, 'interval', minutes=0.25)
        scheduler.start()
    except Exception as e:
        print("upadter->{}".format(e))


def escallate(request):
    try:
        job = Escallate(request).ticket_escallation
        scheduler = BackgroundScheduler()
        scheduler.add_job(job, 'interval', minutes=0.10)
        scheduler.start()
    except Exception as e:
        print("upadter->{}".format(e))
