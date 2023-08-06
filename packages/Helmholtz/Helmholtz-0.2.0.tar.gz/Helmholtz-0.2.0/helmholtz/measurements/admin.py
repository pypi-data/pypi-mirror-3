#encoding:utf-8
from django.contrib import admin
from helmholtz.measurements.models import Parameter

measurements_admin = admin.site

measurements_admin.register(Parameter)
