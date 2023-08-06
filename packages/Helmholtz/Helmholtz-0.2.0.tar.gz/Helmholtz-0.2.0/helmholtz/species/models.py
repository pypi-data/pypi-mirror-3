#encoding:utf-8
from django.db import models

class Species(models.Model):
    """Species of a subject.""" 
    id = models.PositiveIntegerField(primary_key=True, help_text="catalog of life unique identifier")
    scientific_name = models.CharField(max_length=300, unique=True)
    english_name = models.CharField(max_length=300, null=True, blank=True)
    codename = models.CharField(max_length=30, null=True, blank=True)
    lsid = models.TextField(unique=True, null=True, blank=True, help_text="life science identifier")
    url = models.URLField(verify_exists=True, null=True, blank=True)
    
    def __unicode__(self):
        return self.english_name or self.scientific_name
    
    class Meta:
        verbose_name_plural = "species"
        ordering = ['english_name']
 
class Strain(models.Model):
    """Strain of a subject."""
    nomenclature = models.CharField(primary_key=True, max_length=100)
    label = models.CharField(max_length=50, null=True, blank=True)
    species = models.ForeignKey(Species)
    url = models.URLField(verify_exists=True, null=True, blank=True, help_text="web page describing the strain")
    notes = models.TextField(null=True, blank=True) 
    
    class Meta :
        ordering = ['species__english_name', 'label']
    
    def __unicode__(self):
        st = "%s - %s" % (self.species, self.nomenclature)
        if self.label :
            st += " (%s)" % (self.label)
        return st
