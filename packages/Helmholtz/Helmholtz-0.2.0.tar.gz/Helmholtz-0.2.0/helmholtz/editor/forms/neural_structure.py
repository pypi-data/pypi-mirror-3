#encoding:utf-8
from django import forms
from helmholtz.neuralstructures.models import Atlas,BrainRegion,CellType,Cell

class AtlasForm(forms.ModelForm):
    class Meta :
        model = Atlas

class BrainRegionForm(forms.ModelForm):
    class Meta :
        model = BrainRegion

class CellTypeForm(forms.ModelForm):
    class Meta :
        model = CellType

class CellForm(forms.ModelForm):
    class Meta :
        model = Cell