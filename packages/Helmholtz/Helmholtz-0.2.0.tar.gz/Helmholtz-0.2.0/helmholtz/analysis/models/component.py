#encoding:utf-8
################################################################################################################
# List of classes :                                                                                            #
# - Language : Language used to write the component code                                                       #
# - Component : Representation of an analysis type                                                             #
# - SubComponent : Combination of components to realize complex analyses                                       #
################################################################################################################

from django.conf import settings
from django.contrib.contenttypes import generic
from django.db import models
from helmholtz.core.loggers import default_logger

logging = default_logger(__name__)

class Language(models.Model):
    """Language used to write the component code."""
    name = models.CharField(max_length=16, primary_key=True)
    
    class Meta:
        app_label = 'analysis'
    
    def __str__(self):
        return self.name
    
    def __unicode__(self):
        return self.name    

class Component(models.Model) :
    """Representation of an analysis type."""
    label = models.CharField(max_length=256)
    version = models.PositiveIntegerField()
    usecase = models.TextField(null=True, blank=True)
    base = models.BooleanField(default=True)
    language = models.ForeignKey(Language)
    code = models.TextField(null=True, blank=True)
    package = models.TextField(null=True, blank=True)

    def __str__(self) :
        return self.label
    
    def __unicode__(self):
        return self.label
    
    def description(self, format="text"):
        if format == 'text' :
            pass
        elif format == 'html' :
            pass
    
    def get_dependent_components(self, all=[], mainloop=True):
        """Get recursively all components that are depending of the current one."""
        if mainloop : 
            all = []
        for combination in self.is_subcomponent_of.all() :
            combination.component.get_dependent_components(all, mainloop=False)
            all.append(combination.component)
        if mainloop :
            return set(all)
    
    def get_dependent_analyses(self):
        """Get recursively all analyses that are depending of the current component."""
        logging.warning("--- searching analyses using the component %s ---" % (self.id))
        analyses = self.analysis_set.all()
        analyses_list = [k for k in analyses]
        for analysis in analyses : 
            dependent_analyses = analysis.get_dependent_analyses()
            analyses_list.extend(dependent_analyses)
        return analyses_list
    
    def remove_children_analyses(self):
        logging.warning("--- removing analyses using the component %s ---" % (self.id))
        for analysis in self.analysis_set.all() : 
            analysis.remove_children_analyses()
            analysis.remove_potentials()
            analysis.delete()
    
    def remove_encapsulation(self):
        logging.warning("--- removing encapsulation used by component %s ---" % (self.id))
        self.connection_set.all().delete()
        self.pin_set.all().delete()
        self.is_main_component_of.all().delete()
    
    def remove_parent_components(self):
        logging.warning("--- removing components using component %s ---" % (self.id))
        components = self.get_dependent_components()
        for component in components :
            logging.warning("--- removing component %s dependent of %s ---" % (component.id, self.id))
            component.cleanup()
            component.delete()
    
    def cleanup(self):
        logging.warning("--- cleanup component %s ---" % (self.id))
        self.remove_children_analyses()
        self.remove_encapsulation()
        #self.remove_parent_components()    
            
    def get_components_only(self, comp_obj=None, all=[], exclude=None, mainloop=True) :
        if not comp_obj :
            comp_obj = self
        if mainloop : all = []
        base = comp_obj.is_main_component_of.all()
        if exclude :
            base = [k for k in base if k != exclude]
        for combination in base :
            if not combination.subcomponent.base :
                self.get_components_recursively(combination.subcomponent, all, combination.component, mainloop=False)
                all.append(combination.subcomponent)
        if mainloop :
            return all
    
    def get_components_recursively(self, comp_obj=None, all=[], exclude=None, mainloop=True) :
        if not comp_obj :
            comp_obj = self
        if mainloop : all = []
        base = comp_obj.is_main_component_of.all()
        if exclude :
            base = [k for k in base if k != exclude]
        for combination in base :
            if not combination.subcomponent.base :
                self.get_components_recursively(combination.subcomponent, all, combination.component, mainloop=False)
            else :
                all.append(combination.subcomponent)
        if mainloop :
            return all
    
    def n_subcomponents(self) :
        """Number of SubComponents."""
        return len([k for k in self.get_components_recursively()])
    
    def n_pins(self) :
        """Total number of underlying pins."""
        components = [k.subcomponent_id for k in self.component.all()] + [k for k in self.get_components_recursively()]
        return self.pin_set.all().count() + sum([k.pin_set.all().count() for k in components])
    
    def n_connections(self) :
        """Number of connections done into the Component."""
        only = self.get_components_only(exclude=self)
        if not self.base :
            only.append(self)
        schema = [k.connection_set.all() for k in only]
        return sum([len(k) for k in schema])
    
    class Meta:
        app_label = 'analysis'
        unique_together = (('label', 'version'))
        ordering = ('label', 'version')

class SubComponent(models.Model) :
    """Combination of components to realize complex analyses."""
    component = models.ForeignKey(Component, related_name="is_main_component_of")
    subcomponent = models.ForeignKey(Component, related_name="is_subcomponent_of")
    alias = models.CharField(max_length=256)
    
    def __str__(self) :
        return "%s used in %s as %s." % (self.subcomponent, self.component, self.alias)
    
    class Meta:
        app_label = 'analysis'
        unique_together = (('component', 'subcomponent', 'alias'),)
        ordering = ('component', 'subcomponent')
