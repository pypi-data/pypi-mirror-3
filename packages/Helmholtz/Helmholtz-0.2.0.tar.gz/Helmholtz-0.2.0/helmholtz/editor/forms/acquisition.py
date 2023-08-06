#encoding:utf-8
from django import forms
from helmholtz.recording.models import RecordingBlock, ProtocolRecording, RecordingConfiguration
from helmholtz.drug_applications.models import DrugApplication, \
                                        ContinuousDrugApplication, \
                                        DiscreteDrugApplication

class RecordingBlockForm(forms.ModelForm):
    class Meta :
        model = RecordingBlock
        exclude = ['experiment']

class ProtocolRecordingForm(forms.ModelForm):
    class Meta :
        model = ProtocolRecording
        exclude = ['block', 'stimulus']

class RecordingConfigurationForm(forms.ModelForm):
    class Meta :
        model = RecordingConfiguration
        exclude = ['block', 'configuration', 'position', 'measurements']

class DrugApplicationForm(forms.ModelForm):
    class Meta :
        model = DrugApplication
        exclude = ['experiment']

class ContinuousDrugApplicationForm(forms.ModelForm):
    class Meta :
        model = ContinuousDrugApplication
        exclude = ['experiment']

class DiscreteDrugApplicationForm(forms.ModelForm):
    class Meta :
        model = DiscreteDrugApplication
        exclude = ['experiment']
