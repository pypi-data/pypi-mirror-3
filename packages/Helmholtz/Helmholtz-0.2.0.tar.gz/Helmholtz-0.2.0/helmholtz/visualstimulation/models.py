#encoding:utf-8
from django.db import models
from helmholtz.units.fields import PhysicalQuantityField
from helmholtz.stimulation.models import Stimulus

choices = (('B', 'both'), ('L', 'left'), ('R', 'right'))
class VisualStimulus(Stimulus):
    """Store visual stimulus."""
    driven_eye = models.CharField(max_length=1, choices=choices)
    viewing_distance = PhysicalQuantityField(unit='cm', null=True, blank=True)
    
    class Meta:
        verbose_name_plural = 'visual stimuli'

#class ScreenPhotometry(models.Model):
#    """Photometric properties of the stimulus displayed on a screen."""
#    gray_levels = models.IntegerField(null=True, blank=True)
#    luminance_high = PhysicalQuantityField(unit='Cd/m&sup2;', null=True, blank=True)
#    luminance_background = PhysicalQuantityField(unit='Cd/m&sup2;', null=True, blank=True)
#    luminance_low = PhysicalQuantityField(unit='Cd/m&sup2;', null=True, blank=True)
#    
#    class Meta :
#        verbose_name_plural = "screen photometries"
#        
#    def __unicode__(self):
#        return "%s grey levels (%s, %s) with a %s background luminance" % (self.gray_levels, self.luminance_high, self.luminance_low, self.luminance_background)
    
class ScreenArea(models.Model):
    """The screen area corresponding to the receptive field of a :class:`Cell`."""
    position_x = PhysicalQuantityField(unit='&deg;', null=True, blank=True)
    position_y = PhysicalQuantityField(unit='&deg;', null=True, blank=True)
    length = PhysicalQuantityField(unit='&deg;', null=True, blank=True)
    width = PhysicalQuantityField(unit='&deg;', null=True, blank=True)
    orientation = PhysicalQuantityField(unit='&deg;', null=True, blank=True)
    
    def __unicode__(self):
        return "%s x %s area at (%s,%s) coordinates oriented with a %s angle" % (self.length, self.width, self.position_x, self.position_y, self.orientation)
    
#class Bar(models.Model):
#    """Represent a bar moving in front of the subject."""
#    length = PhysicalQuantityField(unit='&deg;', null=True, blank=True)
#    width = PhysicalQuantityField(unit='&deg;', null=True, blank=True)
#    speed = PhysicalQuantityField(unit='&deg;/s', null=True, blank=True)
#    excursion = PhysicalQuantityField(unit='&deg;', null=True, blank=True)
#    
#    def __unicode__(self):
#        return "%s x %s bar moving at %s along a %s excursion" % (self.length, self.width, self.speed, self.excursion)

#For future releases

#from helmholtz.equipment.models import Equipment, DeviceConfiguration
#from helmholtz.electrophysiology.fields import MatrixField

#modes = (
#    ('C', 'color'),
#    ('G', 'greyscales'),
#    ('M', 'monochrome')
#)
#
#ratios = (
#    ('1', '4:3'),
#    ('2', '16:10'),
#    ('3', '16:9'),
#    ('4', '21:9')
#)
#
#technos = (
#    ('CRT', 'cathodic ray tube'),
#    ('LCD', 'liquid crystal display'),
#    ('LED', 'light-emitting diode display'),
#    ('PDP', 'plasma display panels'),
#    ('OLED', 'organic light-emitting diode display'),
#    ('SED', 'surface-conduction electron-emitter display'),
#)
#
#scan_modes = (
#    ('I', 'interlace'),
#    ('P', 'progressive'),
#    ('B', 'both')
#)
# 
#class DisplayDevice(Equipment):
#    """Display device."""
#    frequency = PhysicalQuantityField(unit='Hz', null=True, blank=True)
#    resolution = MatrixField(native_type='integer', dimensions=[2], null=True, blank=True)
#    format = models.CharField(max_length=4, choices=ratios, null=True, blank=True)
#    bits = models.PositiveSmallIntegerField(null=True, blank=True)
#    mode = models.CharField(max_length=1, choices=modes, null=True, blank=True)
#    scan = models.CharField(max_length=1, choices=scan_modes, null=True, blank=True)
#    diagonal = PhysicalQuantityField(unit="cm", null=True, blank=True)
#    display_technology = models.CharField(max_length=10, choices=technos, null=True, blank=True)
#
#scan_modes = (
#    ('I', 'interlace'),
#    ('P', 'progressive')
#)
#class DisplayDeviceConfiguration(DeviceConfiguration):
#    frequency = PhysicalQuantityField(unit='Hz', null=True, blank=True)
#    resolution = MatrixField(native_type='integer', dimensions=[2], null=True, blank=True)
#    format = models.CharField(max_length=4, choices=ratios, null=True, blank=True)
#    bits = models.PositiveSmallIntegerField(null=True, blank=True)
#    mode = models.CharField(max_length=1, choices=modes, null=True, blank=True)
#    scan = models.CharField(max_length=1, choices=scan_modes, null=True, blank=True)
    
#    _labels = {
#        '15C':'high color',
#        '16C':'high color',
#        '24C':'true color',
#        '30C':'deep color',
#        '36C':'deep color',
#        '48C':'deep color'
#    }
    
#    def __unicode__(self):
#        if self.bits == 1 and self.mode == 'M' :
#            mode = "monochrome"
#        else :
#            label_str = "%s%s" % (self.bits, self.mode)
#            tmp = self._labels.get(label_str, 'greyscales')
#            mode = "%s (%s)" % (tmp, self.bits)
#        return "%s x %s in %s format at %s using %s color mode" % (self.resolution[0], self.resolution[1], self.get_format_display(), self.frequency, mode)
