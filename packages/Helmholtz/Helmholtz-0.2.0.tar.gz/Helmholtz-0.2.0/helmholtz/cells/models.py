#encoding:utf-8
from django.db import models
from helmholtz.neuralstructures.models import Cell
from helmholtz.units.fields import PhysicalQuantityField
from helmholtz.recording.models import RecordingBlock
from helmholtz.visualstimulation.models import ScreenArea
from helmholtz.location.models import Position

"""
This module provides models useful to store cell properties.
"""

choices = (('B', 'both'), ('L', 'left'), ('R', 'right'))
class RecordedCell(Cell):
    """`
    Cell characterized by electrophysiolocal techniques :
    
    ``block`` : the block in which the cell is recorded.
    
    ``prefered_orientation`` : ?
    
    ``prefered_direction`` : ?
    
    ``driven_eye`` : ?
    
    ``prefered_speed`` : ?
    
    ``receptive_field`` : ?
    
    ``phase`` : ?
    
    ``spatial_frequency`` : ?
    
    """
    block = models.ForeignKey(RecordingBlock, null=True, blank=True, help_text="if the cell has been characterized by electrophysiology")
    prefered_orientation = PhysicalQuantityField(unit='&deg;', null=True, blank=True)
    prefered_direction = PhysicalQuantityField(unit='&deg;', null=True, blank=True)
    driven_eye = models.CharField(max_length=1, choices=choices, null=True, blank=True)
    prefered_speed = PhysicalQuantityField(unit='&deg;/s', null=True, blank=True)
    receptive_field = models.ForeignKey(ScreenArea, null=True, blank=True)
    phase = PhysicalQuantityField(unit='&deg;', null=True, blank=True)
    spatial_frequency = PhysicalQuantityField(unit='', null=True, blank=True)

class StainedCell(Cell): 
    """Cell identified by stained labelling."""
    position = models.ForeignKey(Position, null=True, blank=True, help_text="if the cell has been identified by stain labelling")
