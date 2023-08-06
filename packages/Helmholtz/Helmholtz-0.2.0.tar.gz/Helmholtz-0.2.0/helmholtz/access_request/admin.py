from django.contrib import admin
from helmholtz.access_request.models import AccessRequest

access_request_admin = admin.site
access_request_admin.register(AccessRequest)

