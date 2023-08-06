#encoding:utf-8
from django.conf import settings
from django.contrib.sites.models import Site
from helmholtz.core.populate import PopulateCommand

sites = [
    {'id':settings.SITE_ID, 'domain':settings.SITE_DOMAIN, 'name':settings.SITE_NAME},
]

class Command(PopulateCommand):
    help = "populate site"
    priority = 0
    data = [
        {'class':Site, 'objects':sites},
    ]
