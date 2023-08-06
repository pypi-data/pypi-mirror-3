#encoding:utf-8
from django.db import models
from django.contrib.contenttypes import generic
from helmholtz.units.fields import PhysicalQuantityField
from helmholtz.core.shortcuts import cast_object_to_leaf_class, get_class
from helmholtz.core.schema import cast_queryset
from helmholtz.core.models import Cast
from helmholtz.access_request.models import AccessRequest
from helmholtz.measurements.models import GenericMeasurement
from helmholtz.equipment.models import DeviceConfiguration, Device 
from helmholtz.experiment.models import Experiment, get_by_types
from helmholtz.stimulation.models import StimulationType, Stimulus
from helmholtz.storage.models import File

class RecordingBlock(models.Model):
    """Split an :class:`Experiment` into several sequences of recording."""
    experiment = models.ForeignKey(Experiment)
    label = models.CharField(max_length=250, null=True, blank=True)
    start = models.DateTimeField(null=True, blank=True)
    end = models.DateTimeField(null=True, blank=True)
    notes = models.TextField(null=True, blank=True)
    
    def __unicode__(self):
        st = "Recording block %s" % self.pk
        if self.label :
            st += " called '%s'" % self.label
        return st
    
    def get_files(self):
        """
        Get :class:`File` instances acquired during the
        execution of the :class:`RecordingBlock` instance.
        """
        cls = get_class('storage', 'File')
        files = cls.objects.filter(signal__recording_channel__protocol__block=self).distinct()
        return files
    files = property(get_files)    
    
    def get_signals(self):
        """
        Get :class:`Signal` instances acquired during the
        execution of the :class:`RecordingBlock` instance.
        """
        cls = get_class('signals', 'Signal')
        signals = cls.objects.filter(recording_channel__protocol__block=self).distinct()
        return signals
    signals = property(get_signals)    
    
    def get_files_and_status_by_protocol_types(self, user):
        """
        Store files relative to the :class:`RecordingBlock`
        instance by protocol type.
        """
        files = dict()
        for file in self.files :
            protocol = file.protocol.type 
            if not (protocol in files) :
                files[protocol] = []
            signals = dict()
            for signal in cast_queryset(file.signal_set.all(), 'ElectricalSignal') :
                if not signal.episode in signals :
                    signals[signal.episode] = list()
                signals[signal.episode].append(signal)
            files[protocol].append({'object':file, 'status':AccessRequest.objects.download_status(file, user), 'signals':signals})
        for protocol in files :
            files[protocol].sort(key=lambda x:x['object'].protocol.pk)
        return files
    
    def get_protocols_by_type(self):
        """
        Store protocols relative to the :class:`RecordingBlock`
        instance by protocol type.
        """
        protocols = {}
        for protocol in self.protocolrecording_set.all() :
            exp_protocol = getattr(protocol.stimulation_type, 'name', None)
            if not (exp_protocol in protocols) :
                protocols[exp_protocol] = []
            protocols[exp_protocol].append(protocol)
        #transform each list of protocol into a QuerySet
        for protocol in protocols : 
            protocols[protocol] = self.protocolrecording_set.model.objects.filter(pk__in=[k.pk for k in protocols[protocol]])
        return protocols
    
    def get_protocols(self):
        """
        Get all :class:`Stimulus` classes relative
        to the :class:`RecordingBlock` instance.
        """
        protocols = self.get_protocols_by_type().keys()
        return protocols
    distinct_protocols = property(get_protocols)
    
    def _protocols(self):
        """
        Return a string containing :class:`Stimulation` 
        subclasses relative to the :class:`RecordingBlock`
        instance.
        """
        protocols = [k.label for k in self.get_protocols()]
        return ','.join(protocols) if protocols else None
    protocol_names = property(_protocols)
    
    def get_methods(self):
        """
        Return recording methods relative to
        the :class:`RecordingBlock` instance
        from relative :class:`RecordingConfiguration`
        objects.
        
        NB : For example only sharp or patch electrode
        configurations are considered as methods. Their
        respective classes having the 'method' property.
        """
        return [k for k in self.configuration_types if hasattr(k, "method")]
    methods = property(get_methods)
    
    def get_configuration_types(self):
        """
        Return recording configurations relative to
        the :class:`RecordingBlock` instance.
        """
        by_types = get_by_types(self, 'equipment', 'deviceconfiguration', 'recordingconfiguration__block')
        return [k for k in by_types.keys()]
    configuration_types = property(get_configuration_types)
    
    def _configurations(self):
        """
        Return a string containing recording configurations names
        relative to the :class:`RecordingBlock` instance.
        """
        methods = [k._meta.verbose_name for k  in self.get_configuration_types()]
        return ', '.join(methods) if methods else None        
    configuration_names = property(_configurations)
    
    def _methods(self):
        """
        Return a string containing recording method names
        relative to the :class:`RecordingBlock` instance.
        """
        methods = [k.method for k  in self.get_methods()]
        return ', '.join(methods) if methods else None        
    method_names = property(_methods)
    
    def get_configurations_by_method_types(self):
        """
        Return the :class:`RecordingConfiguration` instances
        relative to the block by method type.
        """
        configurations = {}
        for configuration in self.recordingconfiguration_set.all() :
            name = cast_object_to_leaf_class(configuration).__class__._meta.verbose_name
            if not (name in configurations) :
                configurations[name] = []
            configurations[name].append(configuration)
        for configuration in configurations :
            configurations[configuration] = self.recordingconfiguration_set.filter(pk__in=[k.pk for k in configurations[configuration]])
        return configurations
    configurations = property(get_configurations_by_method_types)
    
    @property
    def duration(self):
        "Return the duration of a :class:`RecordingBlock` instance."
        return self.end - self.start
    
    @models.permalink
    def get_absolute_url(self):
        return ('helmholtz.recording.views.block_detail', None, {'lab':self.experiment.setup.place.parent.diminutive, 'expt':self.experiment.label, 'block':self.label})

    class Meta:
        ordering = ['experiment__label', 'label']

class RecordingConfiguration(Cast):
    """Configuration of each :class:`Device` used to acquire data."""
    label = models.CharField(max_length=250, null=True, blank=True)
    block = models.ForeignKey(RecordingBlock)
    device = models.ForeignKey(Device)
    configuration = models.ForeignKey(DeviceConfiguration, null=True, blank=True, verbose_name="device configuration")
    measurements = generic.GenericRelation(GenericMeasurement, content_type_field='content_type', object_id_field='object_id')
    
    def __unicode__(self):
        return "%s %s" % (self.cast().__class__._meta.verbose_name, self.label or self.pk)
    
    @property
    def type(self):
        return self.get_subclass()._meta.verbose_name 

mode_choices = (("CC", "current clamp"), ("VC", "voltage clamp"))
class ProtocolRecording(models.Model):
    """
    Split a :class:`RecordingBlock` instance
    into several stimulation protocols.
    """
    block = models.ForeignKey(RecordingBlock)
    label = models.CharField(max_length=250)
    file = models.ForeignKey(File, null=True, blank=True)
    is_continuous = models.NullBooleanField(null=True, blank=True)
    mode = models.CharField(max_length=2, choices=mode_choices, null=True, blank=True)
    number_of_sequences = models.IntegerField(null=True, blank=True)
    sequence_duration = PhysicalQuantityField(unit='ms', null=True, blank=True)
    sequence_delay = PhysicalQuantityField(unit='s', null=True, blank=True)
    stimulation_type = models.ForeignKey(StimulationType)
    stimulation_program = models.CharField(max_length=250, null=True, blank=True)
    stimulus = models.ForeignKey(Stimulus, null=True, blank=True)
    notes = models.TextField(null=True, blank=True)
    measurements = generic.GenericRelation(GenericMeasurement, content_type_field='content_type', object_id_field='object_id')
    
    def get_type(self):
        return self.stimulus.cast().__class__._meta.verbose_name if self.stimulus else 'spontaneous activity'
    type = property(get_type)
    
    def get_methods(self):
        """
        Return recording methods relative to
        the :class:`ProtocolRecording` instance.
        """
        by_types = get_by_types(self, 'equipment', 'deviceconfiguration', 'recordingconfiguration__block__protocolrecording')
        return [k for k in by_types.keys() if hasattr(k, "method")]
    methods = property(get_methods)
    
    def get_method_names(self):
        """
        Return a string containing the recording method names
        relative to the :class:`ProtocolRecording` instance.
        """
        methods = [k.method for k  in self.get_methods()]
        return ', '.join(methods) if self.methods else None  
    method_names = property(get_method_names)
    
    def get_file(self):
        """
        Get :class:`File` instances acquired during the
        execution of the :class:`ProtocolRecording` instance.
        """
        cls = get_class('storage', 'File')
        files = cls.objects.filter(signal__recording_channel__protocol__pk=self.pk).distinct()
        if files.count() :
            return files[0]
        else :
            return None  
    
    def get_files(self):
        """docstring needed."""
        cls = get_class('storage', 'File')
        return cls.objects.filter(signal__recording_channel__protocol=self).distinct()   
    
    def __unicode__(self):
        return "ProcotolRecording %s" % (self.label)
    
    @models.permalink
    def get_absolute_url(self):
        return ('helmholtz.recording.views.protocol_detail', None, {'lab':self.block.experiment.setup.place.parent.diminutive, 'expt':self.block.experiment.label, 'block':self.block.label, 'protocol':self.label})

class RecordingChannel(Cast):
    """Store channels used by the ProtocolRecording instance to make acquisition."""
    label = models.CharField(max_length=250, null=True, blank=True)
    protocol = models.ForeignKey(ProtocolRecording)
    configuration = models.ForeignKey(RecordingConfiguration, null=True, blank=True)
    # channel = models.ForeignKey(Channel)
