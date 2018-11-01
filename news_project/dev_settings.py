from .settings import *

DEBUG = False

SECRET_KEY = 'rjwgw#j6zh%p)-tr(eucw_49*nflldp7_1v2(&0$%y&o3r%-@n'

ALLOWED_HOSTS = ['*']

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    }
}