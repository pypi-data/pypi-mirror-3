#encoding:utf-8
from django.contrib import admin
from helmholtz.stimulation.models import StimulationType, Stimulus

stimulation_admin = admin.site

stimulation_admin.register(StimulationType)
stimulation_admin.register(Stimulus)
