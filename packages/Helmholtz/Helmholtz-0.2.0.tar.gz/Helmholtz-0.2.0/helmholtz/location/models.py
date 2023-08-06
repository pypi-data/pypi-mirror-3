#encoding:utf-8
from django.db import models
from helmholtz.units.fields import PhysicalQuantityField
from helmholtz.neuralstructures.models import BrainRegion#, Atlas
from helmholtz.equipment.models import StereotaxicType

ap_choices = (('A', 'anterior'), ('M', 'medial'), ('P', 'posterior'))
lt_choices = (('L', 'left'), ('R', 'right'))
dv_choices = (('D', 'dorsal'), ('M', 'medial'), ('V', 'ventral'))
class Position(models.Model):
    """Defines a coordinate position relative to an Atlas and an apparatus."""
    label = models.CharField(max_length=20, null=True, blank=True)
    brain_region = models.ForeignKey(BrainRegion, null=True, blank=True)
    apparatus = models.ForeignKey(StereotaxicType, null=True, blank=True)
    ap_axis = models.CharField(max_length=1, choices=ap_choices, null=True, blank=True, help_text="anterior-posterior axis")
    ap_value = PhysicalQuantityField(unit='mm', null=True, blank=True)
    dv_axis = models.CharField(max_length=1, choices=dv_choices, null=True, blank=True, help_text="dorsal-ventral axis")
    dv_value = PhysicalQuantityField(unit='mm', null=True, blank=True)
    lt_axis = models.CharField(max_length=1, choices=lt_choices, null=True, blank=True, help_text="lateral axis")
    lt_value = PhysicalQuantityField(unit='mm', null=True, blank=True)
    depth = PhysicalQuantityField(unit='&micro;m', null=True, blank=True, verbose_name='depth')
    intra = models.BooleanField(default=False)
    
    def _axis(self, prefix):
        """Return a string aggregating the specified axis and the position along this axis."""
        st = ''
        if getattr(self, '%s_axis' % prefix) :
            st += getattr(self, 'get_%s_axis_display' % prefix)()
            value = getattr(self, '%s_value' % prefix)
            if value :
                st += ' (%s)' % value
        return st if st else None
    
    @property
    def ap(self):
        return self._axis('ap')
    
    @property
    def dv(self):
        return self._axis('dv')
    
    @property
    def lt(self):
        return self._axis('lt')
    
    def __unicode__(self):
        pos = "%s-%s-%s" % (self.ap, self.dv, self.lt)
        if self.brain_region is None :
            st = "%s in %s at %s depth" % (pos, self.brain_region, self.depth)
        else :
            st = "%s in %s at %s depth" % (pos, self.brain_region.name_or_abbreviation, self.depth)
        if self.intra :
            st += " (intra)"
        return st

class SpatialConfiguration(models.Model):
    """Defines position of Electrodes, Cameras and Cells 
    relatively to a stereotaxic point defined in Position."""
    label = models.CharField(max_length=20, null=True, blank=True)
    distance_from_surface = PhysicalQuantityField(unit='&micro;m', null=True, blank=True, verbose_name='distance')
    ap_angle = PhysicalQuantityField(unit='rad', null=True, blank=True, verbose_name='anterior-posterior angle')
    lt_angle = PhysicalQuantityField(unit='rad', null=True, blank=True, verbose_name='lateral angle')
    dv_angle = PhysicalQuantityField(unit='rad', null=True, blank=True, verbose_name='dorsal-ventral angle')

    def __unicode__(self):
        return "[%s,%s,%s,%s]" % (self.distance_from_surface, self.ap_angle, self.lt_angle, self.dv_angle) 
