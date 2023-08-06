#encoding:utf-8
from django.contrib import admin
from helmholtz.visualstimulation.models import ScreenArea

visualstimulation_admin = admin.site

visualstimulation_admin.register(ScreenArea)
