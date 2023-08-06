#encoding:utf-8
from django.db import models
from helmholtz.core.models import Cast
from helmholtz.people.models import ScientificStructure, Supplier

"""
This module provides facilities to store store
the set of devices used during experiments or 
useful to deploy a setup. 
"""

class Material(models.Model):
    """
    Material that an :class:`Equipment` instance could be made :
    
    ``name`` : the identifier of the material.
    
    ``composition`` : the chemical composition of the material.
    
    ``supplier`` : the supplier providing the material. 
    """
    name = models.CharField(max_length=256)
    composition = models.CharField(max_length=32, null=True, blank=True)
    supplier = models.ForeignKey(Supplier, null=True, blank=True)
    
    def __unicode__(self):
        return self.name
    
    class Meta:
        ordering = ['name', 'supplier']
        unique_together = (('name', 'supplier'),)


class Equipment(Cast):
    """
    Equipment that could be deployed in a :class:`Setup` :
    
    ``manufacturer`` : the manufacturer or supplier providing the equipment.
    
    ``model`` : the identifier of the equipment.
    
    ``notes`` : notes concerning the equipment.
    
    """
    manufacturer = models.ForeignKey(Supplier, null=True, blank=True)
    model = models.CharField(max_length=20)
    notes = models.TextField(null=True, blank=True)
    
    def __unicode__(self):
        st = self.model
        if self.manufacturer :
            st += " from %s" % (self.manufacturer)
        return st
    
    class Meta :
        verbose_name_plural = 'equipment'


class RecordingPoint(models.Model):
    """
    Part of the equipment useful to acquire data :
    
    
    ``equipment`` : the equipment having this recording point.
    
    ``number`` : the index of the recording point.
    
    ``label`` : the label identifying the recording point.
    
    """
    equipment = models.ForeignKey(Equipment)
    number = models.PositiveSmallIntegerField(default=1)
    label = models.CharField(max_length=50, null=True, blank=True)
    
    def __unicode__(self):
        st = "%s" % self.number
        if self.label :
            st += " called %s" % (self.label)
        return "%s %s of %s" % (self.__class__._meta.verbose_name, st, self.equipment.__unicode__())


class EquipmentType(Cast):
    """
    Type of :class:`Equipment` :
    
    ``name`` : the identifier of the type of equipment.
    """
    name = models.CharField(primary_key=True, max_length=20)
    
    def __unicode__(self):
        return self.name
    
    class Meta :
        ordering = ['name']


class StereotaxicType(EquipmentType):
    """
    Subclass of class:`EquipmentType` to make distinction between
    stereotaxic apparatus and common equipment types.
    """
    
    def __unicode__(self):
        return self.name


class GenericEquipment(Equipment):
    """
    Subclass of Equipment used when it is not necessary to
    describe an :class:`Equipment` instance with metadata.
    """
    type = models.ForeignKey(EquipmentType)


class Software(Equipment):
    """
    Subclass of Equipment to represent software applications.
    """
    name = models.CharField(max_length=100)
    url = models.CharField(max_length=250)
    version = models.CharField(max_length=100)
    compilation_notes = models.CharField(max_length=250)


class Device(Cast):
    """
    Realisation of an :class:`Equipment` :
    
    ``equipment`` : the model of the device.
    
    ``label`` : the label identifying the device.
    
    ``serial_or_id`` : the serial number of the device.
    
    ``notes`` : notes concerning the device.
    """
    equipment = models.ForeignKey(Equipment)
    label = models.CharField(max_length=20)
    serial_or_id = models.CharField(max_length=50, null=True, blank=True)
    notes = models.TextField(null=True, blank=True)
    
    def __unicode__(self):
        return self.label


class DeviceConfiguration(Cast):
    """
    Base class of all kind of configurations making an
    :class:`Equipment` ready for an :class:`Experiment` :
    
    ``label`` : the label identifying the device configuration.
    
    ``notes`` : notes concerning the device configuration.
    """
    label = models.CharField(max_length=50, null=True, blank=True)
    notes = models.TextField(null=True, blank=True)

    def __unicode__(self):
        st = "%s %s" % (self.__class__._meta.verbose_name, self.pk)
        if self.label :
            st += " called '%s'" % self.label 
        return  st


class SubSystem(models.Model):
    """
    Structure :class:`Equipment` used in a
    :class:`Setup` in a hierarchical manner.
    """
    parent = models.ForeignKey('self', null=True, blank=True)
    label = models.CharField(max_length=256)
    devices = models.ManyToManyField(Device, blank=True)
    
    def __unicode__(self):
        return self.label
    
    def get_components(self):
        """
        Return all :class:`SubSystem` instances
        living in the :class:`System` instance.
        """
        result = list()
        subsystems = self.subsystem_set.all()
        for subsystem in subsystems :
            result.append(subsystem)
            result.extend(subsystem.get_components())
        return result
    
    def get_equipment(self):
        """
        Return all :class:`Equipment` instances
        living in the :class:`System` instance.
        """
        equipment = list(self.devices.all())
        subsystems = self.subsystem_set.all()
        for subsystem in subsystems :
            equipment.extend(subsystem.get_equipment())
        return equipment   
    
    class Meta :
        ordering = ['label']


class Setup(models.Model):
    """
    Setup used to launch protocols during an :class:`Experiment` :
    
    ``label`` : the label identifying the setup.
    
    ``room`` : the identifier of the room containing the setup.
    
    ``place`` : the :class:`ScientificStructure` which is the owner of the setup.
    
    """
    label = models.CharField(max_length=30, null=True, blank=True)
    place = models.ForeignKey(ScientificStructure)
    room = models.CharField(max_length=16, null=True, blank=True)
    subsystems = models.ManyToManyField(SubSystem)
    
    def __unicode__(self):
        return u"%s \u2192 %s" % (self.place, self.room)
    
    def get_components(self):
        """
        Return all :class:`SubSystem` instances
        living in the :class:`Setup` instance.
        """
        result = list()
        subsystems = self.subsystems.all()
        for subsystem in subsystems :
            result.append(subsystem)
            result.extend(subsystem.get_components())
        return result
    
    def get_equipment(self):
        """
        Return all :class:`Equipment` instances
        living in the :class:`Setup` instance.
        """
        equipment = list()
        subsystems = self.subsystems.all()
        for subsystem in subsystems :
            equipment.extend(subsystem.get_equipment())
        return equipment
