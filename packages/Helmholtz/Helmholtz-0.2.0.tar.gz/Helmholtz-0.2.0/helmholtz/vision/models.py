#encoding:utf8
from helmholtz.units.fields import PhysicalQuantityField
from helmholtz.preparations.models import PreparationInformation

class AreaCentralis(PreparationInformation):
    """
    Subclass of :class:`PreparationInformation` useful to store the location 
    of the area centralis of an :class:`Animal` both for left and right eyes.
    """
    left_x = PhysicalQuantityField(unit='mm', null=True, blank=True)
    left_y = PhysicalQuantityField(unit='mm', null=True, blank=True)
    right_x = PhysicalQuantityField(unit='mm', null=True, blank=True)
    right_y = PhysicalQuantityField(unit='mm', null=True, blank=True)
          
    class Meta:
        verbose_name_plural = 'area centralis'
    
    def __unicode__(self):
        return "left : (%s, %s), right : (%s, %s)" % (self.left_x, self.left_y, self.right_x, self.right_y)
    
class EyeCorrection(PreparationInformation):
    """
    Subclass of :class:`PreparationInformation` useful to store 
    the eye correction of a :class:`Preparation` used during an :class:`Experiment`.
    """
    left = PhysicalQuantityField(unit='&delta;', null=True, blank=True)
    right = PhysicalQuantityField(unit='&delta;', null=True, blank=True)
        
    class Meta:
        verbose_name_plural = 'eye correction'
    
    def __unicode__(self):
        return "left : %s, right : %s" % (self.left, self.right)
