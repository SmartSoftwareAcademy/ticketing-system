from datetime import datetime
from sched import scheduler
from apscheduler.schedulers.background import BackgroundScheduler
#from .import_email_tickets import import_email
from ticketapp.get_email import EmailDownload
#from django.core.mail.backends.smtp import EmailBackend
from ticketapp.models import *
from ticketapp.views import Escallate
from django.conf import settings
from ticketapp.models import ImapSettings, TicketSettings


ticket_settings = TicketSettings.objects.all().first()


def start(request):
    try:
        imap_settings = ImapSettings.objects.all()[0]
        job = EmailDownload(request, imap_settings.email_id,
                            imap_settings.email_password).login_to_imap_server
        scheduler = BackgroundScheduler()
        scheduler.add_job(job, 'interval', id='extract_mails_job',
                          minutes=0.25, replace_existing=True)
        if imap_settings.auto_import_mails_as_tickets:
            scheduler.start()
        else:
            scheduler.remove_job('extract_mails_job')
    except Exception as e:
        print("upadter->{}".format(e))


def escallate(request):
    try:
        job = Escallate(request).ticket_escallation
        scheduler = BackgroundScheduler()
        scheduler.add_job(job, 'interval', id='escallate_job',
                          minutes=0.10, replace_existing=True)
        if ticket_settings.enable_ticket_escalltion:
            scheduler.start()
        else:
            scheduler.remove_job('escallate_job')
    except Exception as e:
        print("upadter->{}".format(e))
