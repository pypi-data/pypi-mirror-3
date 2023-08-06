#encoding:utf-8
from django import forms
from helmholtz.signals.models import ChannelType, ElectricalRecordingMode

class ChannelTypeForm(forms.ModelForm):
    class Meta :
        model = ChannelType

class ElectricalRecordingModeForm(forms.ModelForm):
    class Meta :
        model = ElectricalRecordingMode
