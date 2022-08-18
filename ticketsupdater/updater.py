from datetime import datetime
from apscheduler.schedulers.background import BackgroundScheduler
from .import_email_tickets import import_email


def start():
    scheduler = BackgroundScheduler()
    scheduler.add_job(import_email, 'interval', minutes=0.25)
    scheduler.start()
