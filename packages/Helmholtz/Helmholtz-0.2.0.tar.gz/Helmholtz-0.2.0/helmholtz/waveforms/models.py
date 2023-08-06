#encoding:utf-8
from django.db import models
from helmholtz.core.models import Cast
from helmholtz.units.fields import PhysicalQuantityField

class Waveform(Cast):
    """Waveform defining an :class:`ElectricalStimulation`."""
    pass

class CurrentStepSequence(Waveform):
    """
    A subclass of :class:`Waveform` corresponding
    to a current step stimulation.
    """
    i_min = PhysicalQuantityField(unit='nA')
    i_step = PhysicalQuantityField(unit='nA')
    n_levels = models.IntegerField(null=True, blank=True)

    def __unicode__(self):
        return "current steps increasing from %s to %s in %d steps" % (self.i_min, self.i_min + (self.n_levels - 1) * self.i_step, self.n_levels)

class PulseSequence(Waveform):
    """
    A subclass of :class:`Waveform` corresponding
    to a pulse sequence stimulation.
    """
    frequency = PhysicalQuantityField(unit='Hz')
    amplitude = PhysicalQuantityField(unit='nA')
    duration = PhysicalQuantityField(unit='ms')
    # pulse_duration unit='µs'

    def __unicode__(self):
        return "pulse sequence at %s, amplitude %s, for %s" % (self.frequency, self.amplitude, self.duration)
