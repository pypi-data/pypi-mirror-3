#encoding:utf-8
from django.contrib import admin
from helmholtz.electricalstimulation.models import ElectricalStimulus

electricalstimulation_admin = admin.site

electricalstimulation_admin.register(ElectricalStimulus)
