import os

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cabot.elaine.dev')
import django.core.handlers.wsgi
application = django.core.handlers.wsgi.WSGIHandler()
