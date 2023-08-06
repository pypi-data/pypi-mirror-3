#encoding:utf-8
from django.contrib import admin
from helmholtz.trackers.models import ConnectionTracker, Message

trackers_admin = admin.site

trackers_admin.register(ConnectionTracker)
trackers_admin.register(Message)
