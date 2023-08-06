#encoding:utf-8
from django import forms
from helmholtz.species.models import Species
from helmholtz.neuralstructures.models import BrainRegion, CellType, Cell

class BrainRegionForm(forms.ModelForm):
    class Meta :
        model = BrainRegion
        exclude = ['parent']

class CellTypeFromBrainRegionForm(forms.ModelForm):
    class Meta :
        model = CellType
        exclude = ['brain_region']

class CellTypeForm(forms.ModelForm):
    class Meta :
        model = CellType

class SpeciesFromBrainRegionForm(forms.ModelForm):
    class Meta :
        model = Species

class BrainRegionFromCellTypeForm(forms.ModelForm):
    class Meta :
        model = BrainRegion

class CellForm(forms.ModelForm):
    class Meta :
        model = Cell
