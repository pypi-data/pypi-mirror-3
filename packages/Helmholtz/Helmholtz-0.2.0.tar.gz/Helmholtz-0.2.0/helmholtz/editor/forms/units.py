#encoding:utf-8
from numpy import array
from django import forms
from helmholtz.electrophysiology.fields import Matrix 
from helmholtz.units.models import BaseUnit, DerivedUnit

class BaseUnitForm(forms.ModelForm):
    
    class Meta :
        model = BaseUnit

class DerivedUnitForm(forms.ModelForm):
    
    class Meta :
        model = DerivedUnit
        exclude = ['base_unit']

class UnitFormField(forms.CharField):
    
    def clean(self, value):    
        return value

class UnitWidget(forms.MultiWidget):
    """
    A Widget that splits a Matrix [2] input into two <input type="text"> boxes.
    """

    def __init__(self, attrs=None):
        widgets = (forms.TextInput(attrs=attrs),
                   forms.TextInput(attrs=attrs))
        super(UnitWidget, self).__init__(widgets, attrs)

    def value_from_datadict(self, data, files, name):
        """File widgets take data from FILES, not POST"""
        values = super(UnitWidget, self).value_from_datadict(data, files, name)
        ar = array(values)
        matrix = Matrix(ar)
        return matrix 

    def decompress(self, value):
        if value:
            return [value.data[0], value.data[1]]
        return [None, None]
