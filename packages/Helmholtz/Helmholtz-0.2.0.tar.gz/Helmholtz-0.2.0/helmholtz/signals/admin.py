#encoding:utf-8
from django.contrib import admin
from helmholtz.signals.models import ChannelType

signals_admin = admin.site

signals_admin.register(ChannelType)
