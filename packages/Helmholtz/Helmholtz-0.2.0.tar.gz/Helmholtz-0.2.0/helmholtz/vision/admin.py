#encoding:utf-8
from django.contrib import admin
from helmholtz.preparations.models import AreaCentralis, EyeCorrection

vision_admin = admin.site

preparations_admin.register(AreaCentralis)
preparations_admin.register(EyeCorrection)
