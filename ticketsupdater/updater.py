from datetime import datetime
from apscheduler.schedulers.background import BackgroundScheduler
#from .import_email_tickets import import_email
from ticketapp.get_email import EmailDownload
from django.core.mail.backends.smtp import EmailBackend
from ticketapp.models import *


def start():
    imap_settings = ImapSettings.objects.all()
    config = OutgoinEmailSettings.objects.all()
    backend = EmailBackend(host=config.email_host, port=config.email_port, username=config.support_reply_email,
                           password=config.email_password, use_tls=config.use_tls, fail_silently=config.fail_silently)
    scheduler = BackgroundScheduler()
    scheduler.add_job(EmailDownload(
        imap_settings.email_id, imap_settings.email_password, config, backend).login_to_imap_server(), 'interval', minutes=0.25)
    scheduler.start()
