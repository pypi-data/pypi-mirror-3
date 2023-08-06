#encoding:utf-8
from django.contrib import admin
from helmholtz.equipment.models import Material, EquipmentType, Equipment, RecordingPoint, StereotaxicType, GenericEquipment, Device, SubSystem, Setup  

equipment_admin = admin.site

#equipment
equipment_admin.register(Material)
equipment_admin.register(EquipmentType)
equipment_admin.register(StereotaxicType)
equipment_admin.register(Equipment)
equipment_admin.register(RecordingPoint)
equipment_admin.register(GenericEquipment)
equipment_admin.register(Device)

#setups
equipment_admin.register(SubSystem)
equipment_admin.register(Setup)
