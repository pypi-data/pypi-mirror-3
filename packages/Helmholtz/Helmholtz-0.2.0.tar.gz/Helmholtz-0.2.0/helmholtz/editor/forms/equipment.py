#encoding:utf-8
from django import forms
from helmholtz.equipment.models import Material, EquipmentType, GenericEquipment, RecordingPoint, Device, StereotaxicType, Setup, SubSystem

class MaterialForm(forms.ModelForm):
    class Meta :
        model = Material
        exclude = ['composition', 'supplier']

class EquipmentTypeForm(forms.ModelForm):
    class Meta :
        model = EquipmentType

class StereotaxicTypeForm(forms.ModelForm):
    class Meta :
        model = StereotaxicType

class GenericEquipmentForm(forms.ModelForm):
    class Meta :
        model = GenericEquipment

class DeviceForm(forms.ModelForm):
    class Meta :
        model = Device
        exclude = ['equipment']

class SetupForm(forms.ModelForm):
    class Meta :
        model = Setup
        exclude = ['subsystems']

class SetupFromStructureForm(forms.ModelForm):
    class Meta :
        model = Setup
        exclude = ['place', 'subsystems']

class SubSystemForm(forms.ModelForm):
    class Meta :
        model = SubSystem
        exclude = ['parent']

class RecordingPointForm(forms.ModelForm):
    class Meta :
        model = RecordingPoint
        exclude = ['equipment']
