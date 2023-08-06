#encoding:utf-8
from django.db import models
from django.db.models import Count
from helmholtz.core.shortcuts import get_class, get_by_types
from helmholtz.core.schema import create_subclass_lookup
from helmholtz.people.models import Researcher
from helmholtz.equipment.models import Setup
from helmholtz.preparations.models import Preparation

class ExperimentType(models.Model):
    """
    The type of an :class:`Experiment` : 
    
    ``name`` : the identifier of the experiment type.
    
    """
    name = models.CharField(primary_key=True, max_length=30)

class Experiment(models.Model):
    """
    Experiment done on a :class:`Preparation` :
    
    ``label`` : the label identifying the experiment.
    
    ``type`` : the type of experiment.
    
    ``start`` : the start timestamp of the experiment.
    
    ``end`` : the end timestamp of the experiment.
    
    ``notes`` : notes concerning the experiment.
    
    ``setup`` : the setup used to make acquisition.
    
    ``researchers`` : researchers participating to the experiment.
    
    ``preparation`` : the preparation which is the subject of the experiment. 
    
    """
    label = models.CharField(max_length=32)
    type = models.ForeignKey(ExperimentType)
    start = models.DateTimeField(null=True, blank=True)
    end = models.DateTimeField(null=True, blank=True)
    notes = models.TextField(null=True, blank=True)
    setup = models.ForeignKey(Setup)
    researchers = models.ManyToManyField(Researcher)
    preparation = models.ForeignKey(Preparation, null=True, blank=True)
    
    def __unicode__(self):
        return self.label if self.label else self.pk
    
    @property
    def duration(self):
        """Return the duration of the :class:`Experiment` instance."""
        if self.start and self.end :
            return (self.end - self.start)
        else :
            return None
     
    def get_files(self):
        """
        Get :class:`File` instances acquired during
        the :class:`Experiment` instance.
        """
        cls = get_class('storage', 'File')
        files = cls.objects.filter(signal__recording_channel__protocol__block__experiment=self).distinct()
        return files
    files = property(get_files)

    @models.permalink
    def get_absolute_url(self):
        return ('helmholtz.experiment.views.experiment_detail', None, {'expt':self.label})
    
    def get_signals(self):
        """
        Get :class:`Signal` instances acquired
        during the :class:`Experiment` instance.
        """
        cls = get_class('signals', 'Signal')
        signals = cls.objects.filter(recording_channel__protocol__block__experiment=self).distinct()
        return signals
    signals = property(get_signals)   
    
    def get_protocols(self):
        """
        Get :class:`ProtocolRecording` instances relative 
        to the :class:`Experiment` instance.
        """
        cls = get_class('recording', 'ProtocolRecording')
        protocols = cls.objects.filter(block__experiment=self).distinct()
        return protocols
    protocols = property(get_protocols)
    
    @property
    def methods(self):
        """
        Return the list of recording methods used
        during the :class:`Experiment` instance.
        """
        by_types = get_by_types(self, 'equipment', 'deviceconfiguration', 'recordingconfiguration__block__experiment')
        return [k for k in by_types.keys() if hasattr(k, "method")]       
    
    def get_protocols_by_type(self):
        """
        Return a dictionary containing all :class:`ProtocolRecording`
        instances relative to the :class:`Experiment` instance
        arranged by protocol type.
        """
        return get_by_types(self, 'stimulation', 'stimulus', 'protocolrecording__block__experiment')
    
    @property
    def protocol_types(self):
        """Get all :class:`ProtocolRecording` types."""
        return self.get_protocols_by_type().keys()
    
    @property
    def method_names(self):
        """Return a string corresponding to the method names."""
        methods = [k.method for k  in self.methods]
        return ', '.join(methods) if methods else None 
    
    @property
    def protocol_names(self):
        """Return a string corresponding to the protocol names."""
        protocols = [k._meta.verbose_name for k in self.protocol_types]
        return ', '.join(protocols) if protocols else None
    
    def get_stimulation_types(self):
        """
        Return the :class:`StimulationType` instances
        to the :class:`Experiment` instance.
        """
        cls = get_class('stimulation', 'StimulationType')
        stim_types = cls.objects.filter(
            protocolrecording__block__experiment__id=self.id).annotate(
                n_protocols=Count('protocolrecording__id', distinct=True
            )
        )
        return stim_types
    stimulation_types = property(get_stimulation_types)
    
    @property
    def stimulation_type_names(self):
        """
        Return a string corresponding to the list of
        stimulation types executed in experiment protocols.
        """
        stim_types = [k.name + " (%s)" % (k.n_protocols) if k.n_protocols else '' for k in self.stimulation_types]
        return ', '.join(stim_types) if stim_types else None 
        
    class Meta:
        ordering = ['-start', 'label']
