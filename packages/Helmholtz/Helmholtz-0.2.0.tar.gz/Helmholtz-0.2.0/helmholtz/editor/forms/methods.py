#encoding:utf-8
import re
from django import forms
from django.core.exceptions import ValidationError
from helmholtz.units.fields import PhysicalQuantity
from helmholtz.location.models import Position,SpatialConfiguration
from helmholtz.electrophysiology.models import DiscElectrodeConfiguration,SharpElectrodeConfiguration,PatchElectrodeConfiguration

class AxisFormField(forms.CharField):
    
    def clean(self,value): 
        pattern = value[1]
        if pattern :
            regexp = "^(\-{0,1})(\d+)(\.\d+){0,1}( \w*){0,1}$"
            match = re.match(regexp,pattern,re.UNICODE)
            if not match :
                raise ValidationError("bad format for the specified physical quantity.")
        return value

ap_choices = (('A', 'anterior'),('M', 'medial'),('P', 'posterior'))
lt_choices = (('L', 'left'),('R', 'right'))
dv_choices = (('D', 'dorsal'),('M', 'medial'),('V', 'ventral'))
class AxisWidget(forms.MultiWidget):

    def __init__(self,attrs=None,choices=()):
        widgets = (forms.Select(attrs=attrs['left'] if attrs.has_key('left') else None,choices=choices),
                   forms.TextInput(attrs=attrs['right'] if attrs.has_key('right') else None))
        super(AxisWidget,self).__init__(widgets,attrs['all'] if attrs.has_key('all') else None)

    def value_from_datadict(self,data,files,name):
        values = super(AxisWidget,self).value_from_datadict(data,files,name)
        return values 

    def decompress(self,value):
        if value:
            raise Exception('test')
            return [value.data[0], value.data[1]]
        return [None,None]

class PositionForm(forms.ModelForm):
    ap_axis = AxisFormField(widget=AxisWidget(attrs={'left':{'class':'form_sub_input_left'},
                                                     'right':{'class':'form_sub_input_right'},
                                                     'all':{}},
                                              choices=ap_choices))
    dv_axis = AxisFormField(widget=AxisWidget(attrs={'left':{'class':'form_sub_input_left'},
                                                     'right':{'class':'form_sub_input_right'},
                                                     'all':{}},
                                              choices=dv_choices))
    lt_axis = AxisFormField(widget=AxisWidget(attrs={'left':{'class':'form_sub_input_left'},
                                                     'right':{'class':'form_sub_input_right'},
                                                     'all':{}},
                                              choices=lt_choices))
    
    class Meta :
        model = Position
        exclude = ['ap_axis',
                   'ap_value',
                   'dv_axis',
                   'dv_value',
                   'lt_axis',
                   'lt_value']
    
    def save(self,commit=True):
        instance = super(PositionForm,self).save(commit)
        #ap
        instance.ap_axis = self.cleaned_data['ap_axis'][0]
        if self.cleaned_data['ap_axis'][1] :
            split = self.cleaned_data['ap_axis'][1].split(' ') 
            instance.ap_value = PhysicalQuantity(float(split[0]),split[1])
        #dv
        instance.dv_axis = self.cleaned_data['dv_axis'][0]
        if self.cleaned_data['dv_axis'][1] :
            split = self.cleaned_data['dv_axis'][1].split(' ') 
            instance.dv_value = PhysicalQuantity(float(split[0]),split[1])
        #lt
        instance.lt_axis = self.cleaned_data['lt_axis'][0]
        if self.cleaned_data['lt_axis'][1] :
            split = self.cleaned_data['lt_axis'][1].split(' ') 
            instance.lt_value = PhysicalQuantity(float(split[0]),split[1])
        instance.save()
        return instance
    
class SpatialConfigurationForm(forms.ModelForm):
    class Meta :
        model = SpatialConfiguration

class DiscElectrodeConfigurationForm(forms.ModelForm):
    class Meta :
        model = DiscElectrodeConfiguration

class SharpElectrodeConfigurationForm(forms.ModelForm):
    class Meta :
        model = SharpElectrodeConfiguration

class PatchElectrodeConfigurationForm(forms.ModelForm):
    class Meta :
        model = PatchElectrodeConfiguration