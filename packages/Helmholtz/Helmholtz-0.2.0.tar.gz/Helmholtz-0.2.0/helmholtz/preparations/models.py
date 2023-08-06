#encoding:utf-8
import datetime
from django.db import models
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes import generic
from helmholtz.core.models import Cast
from helmholtz.species.models import Strain
from helmholtz.people.models import Supplier
from helmholtz.equipment.models import Equipment
from helmholtz.measurements.models import GenericMeasurement, Parameter
from helmholtz.units.fields import PhysicalQuantityField
from helmholtz.chemistry.models import Solution

"""
This module provides a set of classes useful to track
animals living in a laboratory and used for experimentation.
"""

class Animal(models.Model):
    """Animal that is the subject of an :class:`Experiment`."""
    strain = models.ForeignKey(Strain)
    identifier = models.CharField(max_length=15, null=True, blank=True)
    nickname = models.CharField(max_length=15, null=True, blank=True)
    sex = models.CharField(max_length=1, choices=(('M', 'male'), ('F', 'female')), null=True, blank=True)
    birth = models.DateField(help_text="(approximate)", null=True, blank=True)
    sacrifice = models.DateField(null=True, blank=True)
    supplier = models.ForeignKey(Supplier, null=True, blank=True) 
    
    def get_birth(self, age):
        """
        Get the date of birth of the :class:`Animal`
        from an age in days and its sacrifice date.
        """
        assert self.sacrifice, 'sacrifice property unknown'
        delta = datetime.timedelta(age)
        return self.sacrifice - delta
    
    def set_birth(self, age, sacrifice):
        """
        Set the birth date of the :class:`Animal`
        from a sacrifice date and an age.
        """
        delta = datetime.timedelta(age)
        self.birth = sacrifice - delta
        self.save()
    
    def get_sacrifice(self, age): 
        """
        Get the date of sacrifice of the :class:`Animal`
        from an age and its birth date.
        """
        assert self.birth, 'birth property unknown'
        delta = datetime.timedelta(age)
        return self.birth + delta    
    
    def set_sacrifice(self, age, birth):
        """
        Set the sacrifice date of the :class:`Animal`
        from a birth date and an age.
        """
        delta = datetime.timedelta(age)
        self.sacrifice = birth + delta
        self.save()
    
    def _age(self):
        """Age of the :class:`Animal` in weeks."""
        if self.sacrifice and self.birth:
            return round((self.sacrifice - self.birth).days / 7.0, 1)
        else:
            return None
    age = property(_age)
    
    def __unicode__(self):
        st = ''
        if self.identifier :
            st += self.identifier
        if self.strain :
            if self.identifier :
                st += ', '
            st += "%s" % (self.strain)
        if self.sex :
            st += ', ' + self.get_sex_display() 
        age = self._age()
        if age :
            st += ', %s weeks' % age
        return st 
        
    class Meta:
        ordering = ['-sacrifice']



class Preparation(Cast):
    """The subject of an :class:`Experiment`."""
    animal = models.ForeignKey(Animal)
    protocol = models.TextField(null=True, blank=True)   
    observations = generic.GenericRelation(GenericMeasurement, verbose_name="observations", content_type_field='content_type', object_id_field='object_id')
    
    def __unicode__(self):
        cast = self.cast()
        return u"%s, %s" % (cast.__class__._meta.verbose_name, self.animal)
    
    def subclass(self):
        cast = self.cast()
        return cast.__class__._meta.verbose_name
    
    def get_weights(self):
        """Get all measured weights."""
        preparation_type = ContentType.objects.get_for_model(self)
        return GenericMeasurement.objects.filter(parameter__label='weight',
                                                 content_type=preparation_type,
                                                 object_id=self.id)
    
    def get_weight_at_sacrifice(self):
        """Get measured weight at sacrifice."""
        one_hour = datetime.timedelta(0, 3600)
        weights = self.get_weights().filter(timestamp__gte=self.animal.sacrifice - one_hour)
        if weights.count() > 0:
            return weights[weights.count() - 1]
        else:
            return None

    def add_field(self, name, unit):
        """
        Add a metadata field taking a float value to the :class:`Preparation` instance.
        """
        param, created = Parameter.objects.get_or_create(
                            label=name,
                            content_type=ContentType.objects.get_for_model(self),
                            type="F",
                            unit=unit)
        return param



class InVivoPreparation(Preparation):
    """In vivo :class:`Preparation`."""

    class Meta:
        verbose_name = "in vivo"



class InVitroCulture(Preparation):
    """In vitro culture :class:`Preparation`."""
    
    class Meta:
        verbose_name = "in vitro culture"



class InSilico(Preparation):
    """Simulation model :class:`Preparation`."""
    equipment = models.ForeignKey(Equipment, null=True, blank=True)
    model_description = models.TextField()
    
    class Meta:
        verbose_name = "in silico"


          
class InVitroSlice(Preparation):
    """In vitro slice :class:`Preparation`."""
    thickness = PhysicalQuantityField(unit='&mu;m', null=True)
    cut_orientation = models.CharField(max_length=50, null=True, blank=True)
    cutting_solution = models.ForeignKey(Solution, related_name="is_cutting_solution_of", null=True, blank=True)
    bath_solution = models.ForeignKey(Solution, related_name="is_bath_solution_of", null=True, blank=True)
    equipment = models.ForeignKey(Equipment, null=True, blank=True)
    
    class Meta:
        verbose_name = "in vitro slice"


    
class PreparationInformation(Cast):
    """
    Base class of all observations concerning a :class:`Preparation`.
    """
    preparation = models.ForeignKey(Preparation)
