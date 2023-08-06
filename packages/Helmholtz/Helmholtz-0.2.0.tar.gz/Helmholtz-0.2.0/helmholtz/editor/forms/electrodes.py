#encoding:utf-8
from django import forms
from helmholtz.electrophysiology.models import DiscElectrode,SharpElectrode,PatchElectrode

class DiscElectrodeForm(forms.ModelForm):
    class Meta :
        model = DiscElectrode
        exclude = ['external_diameter','impedance']

class SharpElectrodeForm(forms.ModelForm):
    class Meta :
        model = SharpElectrode

class PatchElectrodeForm(forms.ModelForm):
    class Meta :
        model = PatchElectrode