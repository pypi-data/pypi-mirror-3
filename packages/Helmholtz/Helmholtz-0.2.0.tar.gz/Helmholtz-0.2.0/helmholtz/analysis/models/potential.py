#encoding:utf-8
################################################################################################################
# List of classes :                                                                                            #
# - Potential : Input/Output value for a specific analysis                                                     #
################################################################################################################

from django.db import models
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes import generic
from helmholtz.core.models import Cast
from helmholtz.units.fields import PhysicalQuantityField
from helmholtz.units.models import Unit 
from helmholtz.analysis.fields import PickledObjectField
from helmholtz.storage.models import File
from helmholtz.analysis.models.pin import Pin

class Potential(Cast) :
    """Input/Output value for a specific analysis.
    
    NB : In fact the value is defined in subclasses 
    Potential_[Integer,Float,String,Date,Time,DateTime,...,
               ...,Boolean,PhysicalQuantity,PythonObject,Existing]
    
    """
    pin = models.ForeignKey(Pin,db_column='pin') 
    
    class Meta:
        app_label = 'analysis'

class Potential_Existing(Potential) :
    value = models.ForeignKey(Potential,related_name="used_by")
    
    class Meta:
        app_label = 'analysis'

class Potential_Integer(Potential) :
    value = models.IntegerField()
    
    class Meta:
        app_label = 'analysis'
    
    def __str__(self):
        return "%s(%s)" % (self.pin,self.value)
    
    def __unicode__(self):
        return "%s(%s)" % (self.pin,self.value)

class Potential_Float(Potential) :
    value = models.FloatField()
    
    class Meta:
        app_label = 'analysis'
    
    def __str__(self):
        return "%s(%s)" % (self.pin,self.value)
    
    def __unicode__(self):
        return "%s(%s)" % (self.pin,self.value)

class Potential_String(Potential) :
    value = models.TextField()
    
    class Meta:
        app_label = 'analysis'
    
    def __str__(self):
        return "%s(%s)" % (self.pin,self.value)
    
    def __unicode__(self):
        return "%s(%s)" % (self.pin,self.value)

class Potential_Date(Potential) :
    value = models.DateField()
    
    class Meta:
        app_label = 'analysis'
    
    def __str__(self):
        return "%s(%s)" % (self.pin,self.value)
    
    def __unicode__(self):
        return "%s(%s)" % (self.pin,self.value)

class Potential_Time(Potential) :
    value = models.TimeField()
    
    class Meta:
        app_label = 'analysis'
    
    def __str__(self):
        return "%s(%s)" % (self.pin,self.value)
    
    def __unicode__(self):
        return "%s(%s)" % (self.pin,self.value)

class Potential_DateTime(Potential) :
    value = models.DateTimeField()
    
    class Meta:
        app_label = 'analysis'
    
    def __str__(self):
        return "%s(%s)" % (self.pin,self.value)
    
    def __unicode__(self):
        return "%s(%s)" % (self.pin,self.value)

class Potential_Boolean(Potential) :
    value = models.BooleanField()
    
    class Meta:
        app_label = 'analysis'
    
    def __str__(self):
        return "%s(%s)" % (self.pin,self.value)
    
    def __unicode__(self):
        return "%s(%s)" % (self.pin,self.value)

class Potential_PhysicalQuantity(Potential) :
    value = models.FloatField()
    unit = models.ForeignKey(Unit)
    
    class Meta:
        app_label = 'analysis'
    
    def __str__(self):
        return "%s(%s %s)" % (self.pin,self.value,self.unit)
    
    def __unicode__(self):
        return "%s(%s %s)" % (self.pin,self.value,self.unit)

class Potential_PythonObject(Potential) :
    value = PickledObjectField()
    
    class Meta:
        app_label = 'analysis'
    
    def __str__(self):
        return "%s(%s)" % (self.pin,self.value)
    
    def __unicode__(self):
        return "%s(%s)" % (self.pin,self.value)

class Potential_File(Potential) :
    value = models.ForeignKey(File)
    
    class Meta:
        app_label = 'analysis'
    
    def __str__(self):
        return "%s(%s)" % (self.pin,self.value)
    
    def __unicode__(self):
        return "%s(%s)" % (self.pin,self.value)

class Potential_DatabaseObject_Id(Potential):
    content_type = models.ForeignKey(ContentType)
    object_id = models.PositiveIntegerField()
    value = generic.GenericForeignKey('content_type','object_id')
    
    class Meta:
        app_label = 'analysis'
    
    def __str__(self):
        return "%s(%s)" % (self.pin,self.value)
    
    def __unicode__(self):
        return "%s(%s)" % (self.pin,self.value)

class Potential_DatabaseValue_Id(Potential):
    content_type = models.ForeignKey(ContentType)
    object_id = models.PositiveIntegerField()
    object = generic.GenericForeignKey('content_type','object_id')
    field = models.CharField(max_length=64)
    
    class Meta:
        app_label = 'analysis'
    
    def _value(self):
        return getattr(self.object,self.field)
    value = property(_value)
    
    def __str__(self):
        return "%s(%s)" % (self.pin,self.value)
    
    def __unicode__(self):
        return "%s(%s)" % (self.pin,self.value)

class Potential_DatabaseObject_Name(Potential):
    content_type = models.ForeignKey(ContentType)
    object_id = models.TextField()
    value = generic.GenericForeignKey('content_type','object_id')
    
    class Meta:
        app_label = 'analysis'
    
    def __str__(self):
        return "%s(%s)" % (self.pin,self.value)
    
    def __unicode__(self):
        return "%s(%s)" % (self.pin,self.value)

class Potential_DatabaseValue_Name(Potential):
    content_type = models.ForeignKey(ContentType)
    object_id = models.TextField()
    object = generic.GenericForeignKey('content_type','object_id')
    field = models.CharField(max_length=64)
    
    class Meta:
        app_label = 'analysis'
    
    def _value(self):
        return getattr(self.object,self.field)
    value = property(_value)
    
    def __str__(self):
        return "%s(%s)" % (self.pin,self.value)
    
    def __unicode__(self):
        return "%s(%s)" % (self.pin,self.value)