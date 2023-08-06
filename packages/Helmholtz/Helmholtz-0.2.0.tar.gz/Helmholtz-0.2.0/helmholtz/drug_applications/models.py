#encoding:utf-8
from django.db import models
from helmholtz.core.models import Cast
from helmholtz.chemistry.models import Solution, ApplicationType
from helmholtz.experiment.models import Experiment
from helmholtz.units.fields import PhysicalQuantityField

class RouteOfApplication(models.Model):
    """
    Store the route of application used by a :class:`DrugApplication` :
    
    ``name`` : the identifier of the route of application.
    """
    name = models.CharField(max_length=15, primary_key=True)
    
    def __unicode__(self):
        return self.name

class DrugApplication(Cast):
    """
    Store drug applications that could be done on a
    :class:`Preparation` during an :class:`Experiment` :
    
    ``experiment`` : the experiment during which the drug application is done.
    
    ``solution`` : the solution used by the drug application.
    
    ``role`` : the effect of the drug application.
    
    ``route`` : the route of application of the drug application.
    
    ``notes`` : notes concerning the drug application.
    """
    experiment = models.ForeignKey(Experiment)
    solution = models.ForeignKey(Solution)
    role = models.ForeignKey(ApplicationType, null=True, blank=True)
    route = models.ForeignKey(RouteOfApplication, null=True, blank=True) 
    notes = models.TextField(null=True, blank=True)
    
    def __unicode__(self):
        return self._meta.verbose_name + ' ' + str(self.id)
    
class ContinuousDrugApplication(DrugApplication):
    """
    Store drug applications applied during a certain amount
    of time during an :class:`Experiment` on a :class:`Preparation` :
    
    ``start`` : start timestamp of the drug application.
    
    ``end`` : end timestamp of the drug application.
    
    ``rate`` : the rate of the drug application in mL/h by default.
    """
    start = models.DateTimeField(null=True, blank=True) 
    end = models.DateTimeField(null=True, blank=True) 
    rate = PhysicalQuantityField(unit='mL/h', null=True, blank=True) 
     
    def get_duration(self) :
        if self.start and self.end:
            return self.end - self.start
        else:
            return None
    
    class Meta :
        ordering = ['-start']

class DiscreteDrugApplication(DrugApplication):
    """
    Store drug applications applied at a precise moment
    of an :class:`Experiment` on a :class:`Preparation` :
    
    ``time`` : time of the drug application.
    
    ``volume`` : volume of the drug application in ml by default.
    """
    volume = PhysicalQuantityField(unit='ml', null=True, blank=True)
    time = models.DateTimeField(null=True, blank=True)
    
    class Meta :
        ordering = ['-time']
