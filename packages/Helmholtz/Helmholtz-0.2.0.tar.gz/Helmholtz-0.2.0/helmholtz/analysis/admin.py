#encoding:utf-8
from django.contrib import admin
from helmholtz.analysis.models.component import Language,Component
from helmholtz.analysis.models.pin import CodingType,PinType,Pin

analysis_admin = admin.site

analysis_admin.register(Language)
analysis_admin.register(Component)
analysis_admin.register(CodingType)
analysis_admin.register(PinType)
analysis_admin.register(Pin)