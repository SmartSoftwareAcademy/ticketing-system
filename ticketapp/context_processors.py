from .models import System_Settings
from asgiref.sync import *

def get_site_setup(request):
    setup = System_Settings.objects.first()

    return {'setup':setup}