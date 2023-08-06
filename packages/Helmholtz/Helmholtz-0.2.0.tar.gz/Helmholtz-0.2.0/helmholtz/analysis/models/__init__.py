#from analysis import Analysis
#from component import Language,Component,SubComponent
#from configuration import Configuration
#from pin import PinType,CodingType,Pin,Connection
#from potential import Potential,\
#                      Potential_Existing,\
#                      Potential_Integer,\
#                      Potential_Float,\
#                      Potential_String,\
#                      Potential_Date,\
#                      Potential_Time,\
#                      Potential_DateTime,\
#                      Potential_Boolean,\
#                      Potential_PhysicalQuantity,\
#                      Potential_PythonObject,\
#                      Potential_File,\
#                      Potential_DatabaseObject_Id,\
#                      Potential_DatabaseValue_Id,\
#                      Potential_DatabaseObject_Name,\
#                      Potential_DatabaseValue_Name\

#encoding:utf-8
from django.db import models
from django.contrib.contenttypes.models import ContentType

class PinType(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(null=True, blank=True)
    content_type = models.ForeignKey(ContentType)
    
    def __unicode__(self):
        return "%s (%s)" % (self.name, self.content_type.model_class().__name__)
    
    def count_analyses(self):
        return self.is_input_of.count() + self.is_output_of.count() + self.is_parameter_of.count()

class AnalysisType(models.Model):
    name = models.CharField(max_length=100)
    version = models.CharField(max_length=10)
    description = models.TextField(null=True, blank=True)
    inputs = models.ManyToManyField(PinType, related_name="is_input_of")
    parameters = models.ManyToManyField(PinType, related_name="is_parameter_of")
    outputs = models.ManyToManyField(PinType, related_name="is_output_of")
    
    def __unicode__(self):
        return "%s (%s)" % (self.name, self.version)
    
    def count_pins(self):
        return self.inputs.count() + self.outputs.count() + self.parameters.count()
        

class Pin(models.Model):
    pin_type = models.ForeignKey(PinType)
    object_id = models.PositiveIntegerField()
    
    def __unicode__(self):
        obj = self.pin_type.content_type.model_class().get(pk=self.object_id)
        return obj

class Input(Pin):
    pass

class Parameter(Pin):
    pass

class Analysis(models.Model):
    analysis_type = models.ForeignKey(AnalysisType)
    inputs = models.ManyToManyField(Input) 
    parameters = models.ManyToManyField(Parameter)   
    comments = models.TextField()
    
    class Meta :
        verbose_name_plural = "analyses"
    
    def __unicode__(self):
        return "%s - %s - %s" % (self.analysis_type.name, self.analysis_type.version, self.analysis.id)

class Output(Pin):
    analysis = models.ForeignKey(Analysis)

#all kind of values
from helmholtz.units.models import Unit

class IntegerData(models.Model) :
    value = models.IntegerField()
    
    def __unicode__(self):
        return "%s" % (self.value)

class FloatData(models.Model) :
    value = models.FloatField()
    
    def __unicode__(self):
        return "%s" % (self.value)

class StringData(models.Model) :
    value = models.TextField()
    
    def __unicode__(self):
        return "%s" % (self.value)

class DateData(models.Model) :
    value = models.DateField()

    def __unicode__(self):
        return "%s" % (self.value)

class TimeData(models.Model) :
    value = models.TimeField()
    
    def __unicode__(self):
        return "%s" % (self.value)

class DateTimeData(models.Model) :
    value = models.DateTimeField()
    
    def __unicode__(self):
        return "%s" % (self.value)

class BooleanData(models.Model) :
    value = models.BooleanField()
    
    def __unicode__(self):
        return "%s" % (self.value)

class PhysicalQuantityData(models.Model) :
    value = models.FloatField()
    unit = models.ForeignKey(Unit)
    
    def __unicode__(self):
        return "%s %s" % (self.value, self.unit)
