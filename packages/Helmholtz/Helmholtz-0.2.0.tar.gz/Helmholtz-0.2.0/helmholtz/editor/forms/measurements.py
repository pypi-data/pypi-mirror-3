#encoding:utf-8
from django.utils.datastructures import SortedDict
from django import forms
from django.contrib.contenttypes.models import ContentType 
from helmholtz.annotation.models import Descriptor
from helmholtz.measurements.models import Parameter, GenericMeasurement, BoolMeasurement, IntegerMeasurement, FloatMeasurement, StringMeasurement

class ParameterForm(forms.ModelForm):
    class Meta :
        model = Parameter
        exclude = ['constraints']

class DescriptorForm(forms.ModelForm):
    class Meta :
        model = Descriptor

class GenericMeasurementForm(forms.ModelForm):
    class Meta :
        model = GenericMeasurement
        exclude = ['object', 'content_type', 'object_id']

class BoolMeasurementForm(forms.ModelForm):
    class Meta :
        model = BoolMeasurement
        exclude = ['object', 'content_type', 'object_id']

class IntegerMeasurementForm(forms.ModelForm):
    class Meta :
        model = IntegerMeasurement
        exclude = ['object', 'content_type', 'object_id']

class FloatMeasurementForm(forms.ModelForm):
    class Meta :
        model = FloatMeasurement
        exclude = ['object', 'content_type', 'object_id']

class StringMeasurementForm(forms.ModelForm):
    class Meta :
        model = StringMeasurement
        exclude = ['object', 'content_type', 'object_id']

class MeasurementField(forms.Field):
    
    def clean(self, value):
        return value

class MeasurementWidget(forms.MultiWidget):
    """
    A Widget that splits a measurement input into three <input type="text"> boxes.
    """
    def __init__(self, datetime, value_choices, unit_choices, attrs=None):
        widgets = (forms.TextInput(attrs=attrs['left'] if attrs.has_key('left') else None),
                   forms.TextInput(attrs=attrs['right'] if attrs.has_key('right') else None))
        super(MeasurementWidget, self).__init__(widgets, attrs['all'] if attrs.has_key('all') else None)

    def value_from_datadict(self, data, files, name):
        values = super(PhysicalQuantityWidget, self).value_from_datadict(data, files, name)
        return values

    def decompress(self, value):
        if value:
            return [value.value, value.unit]
        return [None, self.initial_unit]
