#encoding:utf-8
#avoid hard coded units and make possible conversion between units
from django.db import models
from helmholtz.core.models import Cast

class Unit(Cast):
    """Store the unit corresponding to a physical quantity."""
    name = models.CharField(max_length=32)
    symbol = models.CharField(max_length=16)
    
    class Meta :
        ordering = ['name']
    
    def __unicode__(self):
        return self.symbol

class BaseUnit(Unit):
    """Store the unit corresponding to a physical quantity."""
    math_symbol = models.CharField(max_length=32, null=True, blank=True)
    physical_meaning = models.TextField()

    #convertions

    def eval_in_term_of_derived_unit(self, value, unit_name):
        """Convert a value corresponding to a :class:`BaseUnit` to its specified :class:`DerivedUnit`."""
        unit = self.unit_set.get(name=unit_name)
        return eval("(%s - %s) / %s" % (value, unit.offset, unit.multiplier)) 

class DerivedUnit(Unit):
    """Store the unit deriving from a :class:`BaseUnit` with the following linear function : multiplier * x + offset."""
    base_unit = models.ForeignKey(BaseUnit)
    multiplier = models.CharField(default="1", max_length=20)
    offset = models.CharField(default="0", max_length=20)
    
    class Meta :
        ordering = ['base_unit__name', 'name']
    
    #delegate math_symbol and physical_meaning to base_unit
    
    def _symbol(self):
        return self.base_unit.math_symbol
    math_symbol = property(_symbol)
    
    def _meaning(self):
        return self.base_unit.physical_meaning
    physical_meaning = property(_meaning)
    
    #convertions
    
    def eval_in_term_of_base_unit(self, value):
        """Convert a value corresponding to a :class:`DerivedUnit` to its relative :class:`BaseUnit`."""
        return eval("%s * %s + %s" % (self.multiplier, value, self.offset))
    
    def eval_in_term_of_derived_unit(self, value, unit_name):
        """Convert a :class:`DerivedUnit` to another one."""
        unit = self.unit_set.get(name=unit_name)
        base_value = "%s * %s + %s" % (self.multiplier, value, self.offset)
        return eval("(%s - %s) / %s" % (base_value, unit.offset, unit.multiplier))
