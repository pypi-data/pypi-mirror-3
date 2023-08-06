#encoding:utf-8
from django.db import models
from helmholtz.units.fields import PhysicalQuantityField 
from helmholtz.storage.models import File
from helmholtz.equipment.models import Equipment, DeviceConfiguration
from helmholtz.chemistry.models import Solution
from helmholtz.location.models import Position
from helmholtz.signals.models import RecordingMode, Signal

class ExposedArea(models.Model):
    anterior_left_corner = models.ForeignKey(Position, related_name='exposedarea_al_corner')
    posterior_right_corner = models.ForeignKey(Position, related_name='exposedarea_pr_corner')

class CameraConfiguration(DeviceConfiguration):
    focus_level = PhysicalQuantityField(unit="", null=True, blank=True)
    under_focus = PhysicalQuantityField(unit="", null=True, blank=True, help_text="distance from the surface where the focus is done") 
    exposed_area = models.ForeignKey(ExposedArea, null=True, blank=True)
    generated_files = models.ManyToManyField(File, null=True, blank=True)
    filter = models.ForeignKey(Equipment, null=True, blank=True)

class VSDOptical(DeviceConfiguration):
    solution = models.ForeignKey(Solution, null=True, blank=True)
    
class IntrinsicOptical(DeviceConfiguration):
    filter = models.CharField(max_length=50, null=True, blank=True)

#channels, recording modes and signals applied to optical imaging

class OpticalRecordingMode(RecordingMode):
    pass

class OpticalSignal(Signal):
    mode = models.ForeignKey(OpticalRecordingMode, null=True, blank=True)
    blocks = models.PositiveIntegerField(default=1)
    trials = models.PositiveIntegerField(default=1)
    
    def __unicode__(self):
        return "%s" % self.pk
