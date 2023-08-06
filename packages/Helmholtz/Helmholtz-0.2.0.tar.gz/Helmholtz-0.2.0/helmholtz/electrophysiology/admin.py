#encoding:utf-8
from django.contrib import admin
from helmholtz.electrophysiology.models import ElectricalRecordingMode, ElectricalChannel, SharpElectrode, PatchElectrode, DiscElectrode, SharpElectrodeConfiguration, PatchElectrodeConfiguration, DiscElectrodeConfiguration, EEG, EKG

electrophysiology_admin = admin.site

#electrical channel types and recording modes
electrophysiology_admin.register(ElectricalRecordingMode)
electrophysiology_admin.register(ElectricalChannel)

#physical electrodes
electrophysiology_admin.register(SharpElectrode)
electrophysiology_admin.register(PatchElectrode)
electrophysiology_admin.register(DiscElectrode)

#electrode configurations
electrophysiology_admin.register(SharpElectrodeConfiguration)
electrophysiology_admin.register(PatchElectrodeConfiguration)
electrophysiology_admin.register(DiscElectrodeConfiguration)
electrophysiology_admin.register(EEG)
electrophysiology_admin.register(EKG)
