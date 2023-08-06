#encoding:utf-8
from django.db import models
from helmholtz.core.models import Cast
from helmholtz.core.shortcuts import cast_object_to_leaf_class
from helmholtz.annotation.fields import QualityField
from helmholtz.recording.models import ProtocolRecording, RecordingConfiguration, RecordingChannel
from helmholtz.storage.models import File
from helmholtz.equipment.models import RecordingPoint

class ChannelType(Cast):
    """Type of a :class:`Channel`, i.e. what it is supposed to acquire."""
    name = models.CharField(max_length=50)
    symbol = models.CharField(max_length=8, null=True, blank=True)
    
    def __unicode__(self):
        return self.symbol if self.symbol else self.name
    
    @property
    def abbr(self):
        if self.name == 'tag' :
            return  'tag_ch'
        elif self.name == 'event' :
            return  'evt_ch'
        else :
            return 'ch'

class RecordingMode(Cast):
    """Recording mode used during a :class:`Signal` acquisition."""
    name = models.CharField(max_length=50)
    
    def __unicode__(self):
        return self.name

class Channel(Cast):
    """Channel from where a :class:`Signal` is acquired."""
    label = models.CharField(max_length=50, null=True, blank=True)
    number = models.PositiveSmallIntegerField(default=1)
    
    def __unicode__(self):
        st = "%s" % self.number
        if self.label :
            return "%s : %s" % (self.label, st)
        return st

class Signal(Cast):
    """Raw data acquired during an :class:`Experiment`."""
    label = models.CharField(max_length=50,null=True, blank=True)
    file = models.ForeignKey(File)
    episode = models.PositiveIntegerField(default=1)
    recording_channel = models.ForeignKey(RecordingChannel, null=True, blank=True)
    recording_point = models.ForeignKey(RecordingPoint, null=True, blank=True)
    quality = QualityField(max=5, null=True, blank=True)
    
    def __unicode__(self):
        return "%s" % self.label
    
    def get_method_type(self):
        return cast_object_to_leaf_class(self.configuration.configuration).__class__._meta.verbose_name.lower()
    method = property(get_method_type)
    
    def get_protocol_type(self):
        return self.protocol.type if self.protocol else None
    protocol_type = property(get_protocol_type)
