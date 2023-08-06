#encoding:utf-8
from django import forms
from helmholtz.recording.models import RecordingBlock, ProtocolRecording, RecordingConfiguration

class RecordingBlockForm(forms.ModelForm):
    class Meta :
        model = RecordingBlock
        exclude = ['experiment']

class ProtocolRecordingForm(forms.ModelForm):
    class Meta :
        model = ProtocolRecording
        exclude = ['block']

class RecordingConfigurationForm(forms.ModelForm):
    class Meta :
        model = RecordingConfiguration
        exclude = ['block']
