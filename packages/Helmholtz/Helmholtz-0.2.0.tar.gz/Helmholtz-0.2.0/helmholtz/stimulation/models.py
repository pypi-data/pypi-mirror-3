#encoding:utf-8
from django.db import models
from helmholtz.core.models import Cast
from helmholtz.equipment.models import Equipment


class StimulationType(models.Model):
    name = models.CharField(max_length=100, primary_key=True)


class Stimulus(Cast):
    """Stimulation presented to/performed on a subject during an Experiment.""" 
    label = models.CharField(max_length=250, null=True, blank=True)
    stimulus_generator = models.ForeignKey(Equipment, null=True, blank=True)
    
    def __unicode__(self):
        st = '%s:%s' % (self.__class__.__name__, self.pk)
        if self.label :
            st += " called '%s'" % self.label
        return st
    
    class Meta:
        verbose_name_plural = 'stimuli'


class SpikeStimulus(Stimulus):
    """Stimulus made of spike, to be used by simulations."""
    type = models.ForeignKey(StimulationType, null=True, blank=True)
    start = models.FloatField(default=0.0, null=True, blank=True)
    duration = models.FloatField(default=0.0, null=True, blank=True)
    notes = models.CharField(max_length=250)

