#encoding:utf-8
from django.core.exceptions import ValidationError
from django.db import models
from helmholtz.electrophysiology.fields import MatrixField
from helmholtz.chemistry.models import Product, Solution
from helmholtz.units.fields import PhysicalQuantityField 
from helmholtz.equipment.models import Equipment, RecordingPoint, Material, DeviceConfiguration
from helmholtz.signals.models import RecordingMode, Signal, ChannelType, Channel
from helmholtz.location.models import Position
from helmholtz.recording.models import RecordingConfiguration, RecordingChannel
#physical electrodes

class Electrode(Equipment):
    """
    A subclass of :class:`Equipment` to store
    electrodes used during experiments :
    
    ``external_diameter`` : the external diameter of the electrode.
    
    ``material`` : the material composing the electrode.
    """
    external_diameter = PhysicalQuantityField(unit='&mu;m', null=True, blank=True)
    material = models.ForeignKey(Material, null=True, blank=True)
    
    def parameters_str(self):
        return "external diameter: %s, material: %s" % (self.external_diameter, self.material)
    
    def __unicode__(self):
        return "%s %s" % (self.__class__.__name__, super(Electrode, self).__unicode__())

class ElectrodeRecordingConfiguration(RecordingConfiguration):
    """
    Configuration of each recording point of an electrode :
    
    ``position`` : location of the electrode during recording.
    """
    position = models.ForeignKey(Position, null=True, blank=True, verbose_name="absolute position") 
    
    def clean(self):
        if self.device.equipment != self.recording_point.equipment :
            raise ValidationError('please choose a recording point compatible with the specified device')

class DiscElectrode(Electrode):
    """Disc electrode equipment."""
    
    def parameters_str(self):
        st = super(DiscElectrode, self).parameters_str()
        return st

class SolidElectrode(Electrode):
    """Solid electrode equipment."""
    impedance = PhysicalQuantityField(unit='M&Omega;', null=True, blank=True)
    
    def parameters_str(self):
        st = super(SolidElectrode, self).parameters_str()
        st += ", impedance: %s" % (self.impedance)
        return st

class HollowElectrode(Electrode):
    """
    Hollow electrode equipment :
    
    ``ìnternal_diameter`` : internal diameter of an hollow electrode that could contain a solution.
    
    """
    internal_diameter = PhysicalQuantityField(unit='&mu;m', null=True, blank=True)
    
    def parameters_str(self):
        st = super(HollowElectrode, self).parameters_str()
        st += ", internal diameter: %s" % (self.internal_diameter)
        return st

class SharpElectrode(HollowElectrode):
    """Sharp electrode equipment."""
    
    def parameters_str(self):
        st = super(SharpElectrode, self).parameters_str()
        return st

class PatchElectrode(HollowElectrode):
    """Patch electrode equipment."""
    
    def parameters_str(self):
        st = super(PatchElectrode, self).parameters_str()
        return st

class MultiElectrode(Electrode):
    """Multielectrode equipment."""
    rows = models.PositiveSmallIntegerField()
    columns = models.PositiveSmallIntegerField()
    step = PhysicalQuantityField(unit='mm')
    
    def parameters_str(self):
        st = super(MultiElectrode, self).parameters_str()
        return st
    
    @property
    def number_of_electrodes(self):
        return self.rows * self.columns

#electrode configurations

class EEG(DeviceConfiguration):
    """EEG configuration"""
    amplification = PhysicalQuantityField(unit='', null=True, blank=True)
    filtering = models.CharField(max_length=50, null=True, blank=True)
    
class EKG(DeviceConfiguration):
    """EKG configuration"""
    amplification = PhysicalQuantityField(unit='', null=True, blank=True)
    filtering = models.CharField(max_length=50, null=True, blank=True)
      
#Maybe ElectrodeConfiguration is too specific whereas the term Electrode is very generic 
class ElectrodeConfiguration(DeviceConfiguration):
    """Base class of all kind of electrode configurations."""
    resistance = PhysicalQuantityField(unit='M&Omega;', null=True, blank=True)
    amplification = models.CharField(max_length=100, null=True, blank=True)
    filtering = models.CharField(max_length=100, null=True, blank=True)
    
    def parameters_str(self):
        return "resistance: %s, amplification: %s, filtering:%s" % (self.resistance, self.amplification, self.filtering)

class DiscElectrodeConfiguration(DeviceConfiguration):
    """ECG or EEG electrode configuration."""
    contact_gel = models.ForeignKey(Product, null=True, blank=True)
    
    def parameters_str(self):
        st = super(DiscElectrodeConfiguration, self).parameters_str()
        st += ", contact gel:%s" % (self.contact_gel)
        return st

class SolidElectrodeConfiguration(ElectrodeConfiguration):
    """Configuration relative to a solid electrode."""
    
    def parameters_str(self):
        st = super(SolidElectrodeConfiguration, self).parameters_str()
        return st

class HollowElectrodeConfiguration(ElectrodeConfiguration):
    """Configuration relative to a hollow electrode."""
    solution = models.ForeignKey(Solution, null=True, blank=True)
    
    def parameters_str(self):
        st = super(HollowElectrodeConfiguration, self).parameters_str()
        st += ", solution:%s" % (self.solution)
        return st

class SharpElectrodeConfiguration(HollowElectrodeConfiguration):
    """Configuration relative to a sharp electrode."""
    
    def parameters_str(self):
        st = super(SharpElectrodeConfiguration, self).parameters_str()
        return st
    
    method = "sharp"

configurations = (('CA', 'cell attached'),
                  ('WC', 'whole cell'),
                  ('PP', 'perforated patch'),
                  ('IO', 'inside out'),
                  ('OO', 'outside out'),
                  ('L', 'loose'))
class PatchElectrodeConfiguration(HollowElectrodeConfiguration):
    """Configuration relative to a patch electrode."""
    seal_resistance = PhysicalQuantityField(unit='M&Omega;', null=True, blank=True)
    contact_configuration = models.CharField(max_length=2, choices=configurations, null=True, blank=True)
    
    def parameters_str(self):
        st = super(PatchElectrodeConfiguration, self).parameters_str()
        st += ", seal resistance:%s" % (self.seal_resistance)
        st += ", contact configuration:%s" % (self.get_contact_configuration_display())
        return st

    method = "patch"

#channels, recording modes and signals applied to electrophysiology
class ElectricalChannelType(ChannelType):
    """Type of an electrical channel, i.e. what it is supposed to acquire."""
    pass
  
class ElectricalRecordingMode(RecordingMode):
    """Recording mode used during an electrical signal acquisition."""
    pass

class ElectricalChannel(Channel):
    """Channel from where an electrical signal is acquired."""
    type = models.ForeignKey(ElectricalChannelType, null=True, blank=True)
    
    def __unicode__(self):
        st = super(ElectricalChannel, self).__unicode__()
        if self.type :
            st += "(%s)" % (self.type)
        return st

class AmplifierConfiguration(DeviceConfiguration):
    """
    Store configurations of amplifiers used during acquisition.
    """
    amplification = PhysicalQuantityField(unit="dB", null=True, blank=True)
    filtering = models.CharField(max_length=100, null=True, blank=True)
    channel_type = models.ForeignKey(ElectricalChannelType, null=True, blank=True)

class ElectricalRecordingChannel(RecordingChannel):
    """
    A subclass of :class:`RecordingChannel` to store the recording channel properties :
    
    ``channel`` : the acquisition card channel relative to the signal.
    
    ``mode`` : the recording mode.
    
    ``amplification`` : the amplification configuration applied to the actual signal.
    
    ``units`` : x and y coordinates units.
    """
    channel = models.ForeignKey(ElectricalChannel)
    mode = models.ForeignKey(ElectricalRecordingMode, null=True, blank=True)
    amplification = models.ForeignKey(AmplifierConfiguration, null=True, blank=True)
    units = MatrixField(native_type='varchar', dimensions=[2])

    @property
    def x_unit(self):
        return self.units.data[0]
    
    @property
    def y_unit(self):
        return self.units.data[1] 

class ElectricalSignal(Signal):
    """
    A subclass of :class:`Signal` to store raw
    data acquired with an electrode based system.
    """
    
    def __unicode__(self):
        return "%s" % self.pk

    class Meta :
        proxy = True
    
    def duration(self): 
        return self.analyses.get(input_of__label__icontains="duration").input_of.get().outputs.get().cast().value
    
    def min(self):
        return self.analyses.get(input_of__label__icontains="min").input_of.get().outputs.get().cast().value
    
    def max(self):
        return self.analyses.get(input_of__label__icontains="max").input_of.get().outputs.get().cast().value
    
    def p2p(self):
        return self.analyses.get(input_of__label__icontains="p2p").input_of.get().outputs.get().cast().value
    
    def amplitude(self):
        return self.analyses.get(input_of__label__icontains="amplitude").input_of.get().outputs.get().cast().value
    
    def mean(self):
        return self.analyses.get(input_of__label__icontains="mean").input_of.get().outputs.get().cast().value
    
    def std(self):
        return self.analyses.get(input_of__label__icontains="std").input_of.get().outputs.get().cast().value
    
    def rms(self):
        return self.analyses.get(input_of__label__icontains="rms").input_of.get().outputs.get().cast().value
    
    def var(self):
        return self.analyses.get(input_of__label__icontains="var").input_of.get().outputs.get().cast().value
