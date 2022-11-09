import os
import sys
from ticket_system.wsgi import application
from whitenoise import WhiteNoise


sys.path.insert(0, os.path.dirname(__file__))

environ = os.environ.setdefault(
    "DJANGO_SETTINGS_MODULE", "ticket_system.settings")

application = WhiteNoise(
    application, root="/home/masters1/public_html/ticketing-system/static/")

application.add_files(
    "/home/masters1/public_html/ticketing-system/static/", prefix="more-files/")
