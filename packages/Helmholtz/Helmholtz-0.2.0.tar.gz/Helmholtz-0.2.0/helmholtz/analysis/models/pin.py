#encoding:utf-8
################################################################################################################
# List of classes :                                                                                            #
# - Pin : Input/Outpus relative to a component                                                                 #
# - PinType : Define if a pin is an Input,Output,Debug or Parameter to have more granularity in IO definition  #
# - CodingType : Coding of a pin, i.e. the kind of value that it will receive                                  #
# - Connection : Connection schema useful to combine components                                                #
################################################################################################################

from django.db import models
from helmholtz.analysis.models.component import Component,SubComponent

class PinType(models.Model) :
    """Define if a pin is an Input,Output,Debug or Parameter."""
    name = models.CharField(primary_key=True,max_length=32)
    
    class Meta:
        app_label = 'analysis'
    
    def __str__(self):
        return self.name
    
    def __unicode__(self):
        return self.name

class CodingType(models.Model) :
    """Coding of an input/output."""
    name = models.CharField(primary_key=True,max_length=32)

    class Meta:
        app_label = 'analysis'

    def __str__(self):
        return self.name
    
    def __unicode__(self):
        return self.name

class Pin(models.Model) :
    """Inputs/Outputs relative to a component."""
    component = models.ForeignKey(Component)
    label = models.CharField(max_length=256)
    usecase = models.TextField(null=True,blank=True)
    pintype = models.ForeignKey(PinType)
    codingtype = models.ForeignKey(CodingType,null=True,blank=True)
    
    class Meta:
        app_label = 'analysis'
        unique_together = (('component','label'),)
        ordering = ('component','label')
    
    def __str__(self):
        return "%s.%s" % (self.component,self.label)
    
    def __unicode__(self):
        return "%s.%s" % (self.component,self.label)
        
class Connection(models.Model) :
    """Connection schema useful to combine components."""
    component = models.ForeignKey(Component)
    pin_left = models.ForeignKey(Pin,related_name="pin_left")
    pin_right = models.ForeignKey(Pin,related_name="pin_right")
    alias_left = models.ForeignKey(SubComponent,related_name="alias_left",null=True,blank=True)
    alias_right = models.ForeignKey(SubComponent,related_name="alias_right",null=True,blank=True)
    
    class Meta:
        app_label = 'analysis'
        ordering = ('id','component')
    
    def __str__(self):
        return "%s(%s.%s,%s.%s)" % (self.component,self.alias_left.alias,self.pin_left,self.alias_right.alias,self.pin_right)
    
    def __unicode__(self):
        return "%s(%s.%s,%s.%s)" % (self.component,self.alias_left.alias,self.pin_left,self.alias_right.alias,self.pin_right)
        