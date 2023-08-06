#encoding:utf-8
from django.db import models
from helmholtz.stimulation.models import Stimulus
from helmholtz.electrophysiology.models import ElectrodeRecordingConfiguration
from helmholtz.waveforms.models import Waveform

class ElectricalStimulus(Stimulus):
    """
    A subclass of :class:`Stimulus` to store electrical stimuli :
    
    ``electrode`` : a reference the :class:`ElectrodeRecordingConfiguration` generating the stimulation.
    
    ``waveform`` : the waveform of the stimulation.
    """
    electrode = models.ForeignKey(ElectrodeRecordingConfiguration, null=True)
    waveform = models.ForeignKey(Waveform)
