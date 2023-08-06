from django import forms
from helmholtz.annotation.fields import QualityFormField 
from helmholtz.editor.forms.units import UnitFormField, UnitWidget
from helmholtz.electrophysiology.models import SharpElectrode, PatchElectrode, SolidElectrode, ElectrodeRecordingConfiguration, ElectricalSignal, ElectricalChannelType, ElectricalRecordingMode, ElectricalChannel, SolidElectrodeConfiguration, SharpElectrodeConfiguration, PatchElectrodeConfiguration, EEG, EKG

class ElectrodeRecordingConfigurationForm(forms.ModelForm):
    class Meta :
        model = ElectrodeRecordingConfiguration
        exclude = ['block']

class SharpElectrodeForm(forms.ModelForm):
    class Meta :
        model = SharpElectrode

class PatchElectrodeForm(forms.ModelForm):
    class Meta :
        model = PatchElectrode

class SolidElectrodeForm(forms.ModelForm):
    class Meta :
        model = SolidElectrode

class ElectricalChannelTypeForm(forms.ModelForm):
    class Meta :
        model = ElectricalChannelType

class ElectricalChannelForm(forms.ModelForm):
    
    class Meta :
        model = ElectricalChannel

class ElectricalRecordingModeForm(forms.ModelForm):
    class Meta :
        model = ElectricalRecordingMode

class ElectricalSignalFromProtocolForm(forms.ModelForm):
    units = UnitFormField(max_length=5, widget=UnitWidget(attrs={'class':'form_unit_input'}))
    
    class Meta :
        model = ElectricalSignal
        exclude = ['protocol']

class ElectricalSignalForm(forms.ModelForm):
    units = UnitFormField(max_length=5, widget=UnitWidget(attrs={'class':'form_unit_input'}))
    
    class Meta :
        model = ElectricalSignal
        exclude = ['protocol']

#class ElectricalSignalFromProtocolForm(forms.ModelForm):
#    units = UnitFormField(max_length=5, widget=UnitWidget())
# 
#    class Meta :
#        model = ElectricalSignal
#        exclude = ['configuration', 'protocol', 'mode', 'channel_type']
#        widgets = {'quality':QualityWidget()}

class SolidElectrodeConfigurationForm(forms.ModelForm):
    class Meta :
        model = SolidElectrodeConfiguration

class SharpElectrodeConfigurationForm(forms.ModelForm):
    class Meta :
        model = SharpElectrodeConfiguration

class PatchElectrodeConfigurationForm(forms.ModelForm):
    class Meta :
        model = PatchElectrodeConfiguration

class EEGConfigurationForm(forms.ModelForm):
    class Meta :
        model = EEG

class EKGConfigurationForm(forms.ModelForm):
    class Meta :
        model = EKG
