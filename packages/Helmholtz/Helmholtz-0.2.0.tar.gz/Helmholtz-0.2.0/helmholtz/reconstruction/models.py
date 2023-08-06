#encoding:utf-8
from django.db import models
from helmholtz.neuralstructures.models import Cell
from helmholtz.storage.models import File
from helmholtz.annotation.fields import QualityField
from helmholtz.annotation.models import StaticDescription

class Reconstruction(models.Model):
	"""Reconstruction of a :class:`Cell`."""
	date = models.DateTimeField()
	cell = models.ForeignKey(Cell)
	file = models.ForeignKey(File)
	quality = QualityField(max=5, null=True)
	comments = models.TextField(null=True, blank=True)
	description = models.ManyToManyField(StaticDescription, null=True) # il peut y avoir plus d'une seule description
