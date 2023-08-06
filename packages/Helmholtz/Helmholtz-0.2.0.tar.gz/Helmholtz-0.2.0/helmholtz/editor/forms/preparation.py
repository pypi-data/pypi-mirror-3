#encoding:utf-8
from django import forms
from helmholtz.preparations.models import Animal, Preparation, InVivoPreparation, InVitroCulture, InSilico, InVitroSlice, PreparationInformation
from helmholtz.vision.models import AreaCentralis, EyeCorrection

class AnimalForm(forms.ModelForm):
    class Meta :
        model = Animal

class PreparationBaseForm(forms.ModelForm):
    class Meta :
        model = Preparation

class PreparationForm(forms.ModelForm):
    class Meta :
        model = Preparation
        exclude = ['experiment']

class InVivoForm(forms.ModelForm):
    class Meta :
        model = InVivoPreparation
        #exclude = ['experiment']

class InVitroCultureForm(forms.ModelForm):
    class Meta :
        model = InVitroCulture
        exclude = ['experiment']

class InSilicoForm(forms.ModelForm):
    class Meta :
        model = InSilico
        exclude = ['experiment']

class InVitroSliceForm(forms.ModelForm):
    class Meta :
        model = InVitroSlice
        exclude = ['experiment']

class PreparationInformationForm(forms.ModelForm):
    class Meta :
        model = PreparationInformation

class AreaCentralisForm(forms.ModelForm):
    class Meta :
        model = AreaCentralis
        exclude = ['preparation']

class EyeCorrectionForm(forms.ModelForm):
    class Meta :
        model = EyeCorrection
        exclude = ['preparation']
