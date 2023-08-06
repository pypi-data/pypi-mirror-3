#encoding:utf-8
from django.db import models
from helmholtz.core.models import Cast
from helmholtz.equipment.models import Equipment
from helmholtz.chemistry.models import Solution
from helmholtz.units.fields import PhysicalQuantityField
from helmholtz.experiment.models import Experiment

class HistoChemistryStep(Cast):
    """Step composing an HistoChemistry."""
    experiment = models.ForeignKey(Experiment)
    previous_step = models.ForeignKey('self')
    notes = models.TextField(null=True, blank=True)

class BathStep(HistoChemistryStep):
    duration = models.TimeField(null=True, blank=True)
    temperature = PhysicalQuantityField(unit="°", null=True, blank=True)
    solution = models.ForeignKey(Solution, related_name="is_solution_of_bath_steps", null=True, blank=True)

cutting_plane = (('P', 'parasagittal'), ('H', 'horizontal'), ('V', 'vertical'))
class CuttingStep(HistoChemistryStep):
    equipment = models.ForeignKey(Equipment)
    temperature = PhysicalQuantityField(unit="°", null=True, blank=True)
    thickness = PhysicalQuantityField(unit='&mu;m', null=True)
    cut_orientation = models.CharField(max_length=1, choices=cutting_plane, null=True, blank=True)
    cutting_solution = models.ForeignKey(Solution, related_name="is_solution_of_cutting_steps", null=True, blank=True)
