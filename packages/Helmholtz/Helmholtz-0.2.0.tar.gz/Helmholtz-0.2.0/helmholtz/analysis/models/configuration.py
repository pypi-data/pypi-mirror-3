#encoding:utf-8
################################################################################################################
# List of classes :                                                                                            #
# - Configuration : Input/Output value for a specific analysis                                                 #
################################################################################################################

from django.db import models
from helmholtz.analysis.models.component import Component
from helmholtz.analysis.models.potential import Potential

class Configuration(models.Model) :
    """Fixed parameters between 2 successive analysis."""
    component = models.ForeignKey(Component)
    potentials = models.ManyToManyField(Potential,related_name="config_of")
#    comments = models.TextField(null=True,blank=True)
    
    class Meta:
        app_label = 'analysis'
    
    def __str__(self):
        return self.id
    
    def __unicode__(self):
        return self.id
    
    def description(self,format="text"):
        assert format in ["text","html"]
        if format == "text":
            pass
        else :
            pass

