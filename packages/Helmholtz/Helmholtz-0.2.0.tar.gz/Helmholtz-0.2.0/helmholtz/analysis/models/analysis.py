#encoding:utf-8
################################################################################################################
# List of classes :                                                                                            #
# - Analysis : State of a component inputs/outputs/configuration fixed for a specific analysis                 #
################################################################################################################

from django.conf import settings
from django.db import models
from helmholtz.analysis.models.component import Component
from helmholtz.analysis.models.potential import Potential, Potential_Existing
from helmholtz.analysis.models.configuration import Configuration
from helmholtz.core.loggers import default_logger

logging = default_logger(__name__)

class Analysis(models.Model) :
    """State of a component inputs/outputs/configuration fixed for a specific analysis."""
    label = models.CharField(max_length="256")
    component = models.ForeignKey(Component)
    configuration = models.ForeignKey(Configuration, null=True, blank=True)
    inputs = models.ManyToManyField(Potential, related_name="input_of")
    outputs = models.ManyToManyField(Potential, related_name="output_of")
    comments = models.TextField(null=True, blank=True)
    
    def __str__(self):
        return "%s : %s" % (self.id, self.label) if self.label else self.id
    
    def __unicode__(self):
        return "%s : %s" % (self.id, self.label) if self.label else self.id
    
    def description(self, format="text"):
        if format == 'text' :
            pass
        elif format == 'html' :
            pass
    
    def get_dependent_analyses(self, all=[], mainloop=True):
        if mainloop : 
            all = []
        for output in self.outputs.all() :
            existing_potentials = Potential_Existing.objects.filter(value=output)
            for potential in existing_potentials :
                analysis = [k for k in potential.input_of.all()]
                assert len(analysis) < 2, "too many analyses linked to the input"
                if len(analysis) > 0 :
                    if not (analysis[0] in all) :
                        all.extend(analysis)   
                    analysis[0].get_dependent_analyses(all, mainloop=False)       
        if mainloop :
            return list(set(all))
    
    def remove_potentials(self):
        logging.warning("removing inputs and outputs of analysis %s" % (self.label))
        self.inputs.all().delete()
        self.outputs.all().delete()
        if self.configuration :
            self.configuration.potentials.all().delete()
            self.configuration.delete()
    
    def remove_children_analyses(self):
        analyses = self.get_dependent_analyses()
        for analysis in analyses :
            logging.warning("removing analysis %s dependent of %s" % (analysis.label if analysis.label else analysis.id, self.label if self.label else self.id))
            analysis.remove_potentials()
            analysis.delete()
   
    class Meta:
        app_label = 'analysis'
        ordering = ('label', 'id')
