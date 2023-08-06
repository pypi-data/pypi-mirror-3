#encoding:utf-8
import re
from django import forms
from django.forms import Select, TextInput
from django.core.exceptions import ValidationError
from helmholtz.units.models import Unit
from helmholtz.units.fields import PhysicalQuantity
from helmholtz.location.models import Position

class AxisWidget(forms.MultiWidget):

    def __init__(self, attrs=None, choices=()):
        widgets = (forms.Select(attrs=attrs['left'] if attrs.has_key('left') else None, choices=choices),
                   forms.TextInput(attrs=attrs['middle'] if attrs.has_key('middle') else None),
                   forms.TextInput(attrs=attrs['right'] if attrs.has_key('right') else None))
        super(AxisWidget, self).__init__(widgets, attrs['all'] if attrs.has_key('all') else None)

    def value_from_datadict(self, data, files, name):
        values = super(AxisWidget, self).value_from_datadict(data, files, name)
        return values 

    def decompress(self, value):
        if value:
            return [value[0], value[1], value[2]]
        return [None, None, None]

class AxisFormField(forms.Field):
    
    def clean(self, value):
        if value[1] :
            try :
                return [value[0], float(value[1]), value[2]]
            except :
                raise ValidationError('please specify a numeric value')
        return value

attrs = {
    'left':{'class':'form_sub_input_axis_choice'},
    'middle':{'class':'form_sub_input_axis_value'},
    'right':{'class':'form_sub_input_axis_unit'},
    'all':{}
}

#init choices for each axis
ap_choices = (('A', 'anterior'), ('M', 'medial'), ('P', 'posterior'))
dv_choices = (('D', 'dorsal'), ('M', 'medial'), ('V', 'ventral'))
lt_choices = (('L', 'left'), ('R', 'right'))

class PositionForm(forms.ModelForm):
    ap = AxisFormField(label='Antero-posterior axis', widget=AxisWidget(attrs=attrs, choices=ap_choices))
    dv = AxisFormField(label='Dorso-ventral axis', widget=AxisWidget(attrs=attrs, choices=dv_choices))
    lt = AxisFormField(label='Lateral axis', widget=AxisWidget(attrs=attrs, choices=lt_choices))
    
    def _get_quantity_axis(self, instance, prefix):
        """Return instance axis and the PhysicalQuantity corresponding to coordinates along this axis."""
        if instance :
            return getattr(self.instance, '%s_value' % prefix, None), getattr(self.instance, '%s_axis' % prefix)
        else :
            return None, None
    
    def _get_value_unit(self, quantity, prefix):
        """Return value and unit of a PhysicalQuantity."""
        if quantity :
            return quantity.value, quantity.unit
        else :
            #if quantity is None 
            #return the default unit
            return None, self._meta.model._meta.get_field_by_name('%s_value' % prefix)[0].unit
    
    def _get_axis_value_unit(self, prefix):
        """docstring needed."""
        instance = getattr(self, 'instance', None)
        quantity, axis = self._get_quantity_axis(instance, prefix)
        value, unit = self._get_value_unit(quantity, prefix)
        return axis, value, unit
    
    def __init__(self, *args, **kwargs) :
        #call base class __init__
        super(PositionForm, self).__init__(*args, **kwargs)
        
        #deduce initial values from current instance
        self.fields['ap'].initial = self._get_axis_value_unit('ap')
        self.fields['dv'].initial = self._get_axis_value_unit('dv')
        self.fields['lt'].initial = self._get_axis_value_unit('lt')
    
    class Meta :
        model = Position
        exclude = ['ap_axis',
                   'ap_value',
                   'dv_axis',
                   'dv_value',
                   'lt_axis',
                   'lt_value'
        ]
    
    def get_quantity(self, prefix):
        """Return a PhysicalQuantity from the second and third widgets."""
        if self.cleaned_data[prefix][1] :
            return PhysicalQuantity(self.cleaned_data[prefix][1], self.cleaned_data[prefix][2])
        return None

    def set_axis(self, instance, prefix):
        """Set instance axis properties from the 3 widgets."""
        setattr(instance, '%s_axis' % prefix, self.cleaned_data[prefix][0])
        quantity = self.get_quantity(prefix)
        setattr(instance, '%s_value' % prefix, quantity)
    
    def save(self, commit=True):
        instance = super(PositionForm, self).save(commit)
        self.set_axis(instance, 'ap')
        self.set_axis(instance, 'dv')
        self.set_axis(instance, 'lt')
        instance.save()
        return instance
