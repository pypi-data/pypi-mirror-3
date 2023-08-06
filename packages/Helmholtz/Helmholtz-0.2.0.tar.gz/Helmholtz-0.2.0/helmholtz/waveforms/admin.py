#encoding:utf-8
from django.contrib import admin
from helmholtz.waveforms.models import PulseSequence, CurrentStepSequence, Waveform

waveforms_admin = admin.site

waveforms_admin.register(PulseSequence)
waveforms_admin.register(CurrentStepSequence)
waveforms_admin.register(Waveform)
