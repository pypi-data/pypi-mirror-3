#encoding:utf-8
from django import forms
from helmholtz.species.models import Species,Strain

class SpeciesForm(forms.ModelForm):
    class Meta :
        model = Species

class StrainForm(forms.ModelForm):
    class Meta :
        model = Strain
        exclude = ['species']