#encoding:utf-8
from django.db import models
from django.db.models.base import ModelBase
from django.contrib.contenttypes.models import ContentType
from helmholtz.core.models import Cast, HierarchicalStructure

class Node(Cast, HierarchicalStructure):
    """Base class of nodes composing a hierarchical structure."""
    position = models.PositiveSmallIntegerField(default=0)
    parent = models.ForeignKey('self', related_name="children", null=True, blank=True)
    
    class Meta:
        ordering = ['position']
    
    def __unicode__(self):
        return self.cast().__unicode__()
        
class View(Node):
    """The root node of a hierarchical structure."""
    name = models.CharField(max_length=256)
    update = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['id']
    
    def __unicode__(self):
        return self.name

class Section(Node):
    """Split the hierarchical structure into themes."""
    title = models.CharField(max_length=256)
    
    def __unicode__(self):
        return "section : %s" % self.title

class Entity(Node): #future name : ModelClass
    """Store classes that could be grouped under a specific theme."""
    content_type = models.ForeignKey(ContentType)
    field_name = models.CharField(max_length=500, null=True, blank=True, help_text="useful to differenciate two fields pointing to the same class")

    class Meta:
        ordering = ['position']
        verbose_name_plural = 'entities'

    def __unicode__(self):
        return "model : %s" % (self.content_type.model_class())
    
    def get_child_entity(self, cls, key=None):
        #key make differenciation between two same entities
        #but originating from different fields
        _ct = ContentType.objects.get_for_model(cls)
        schemata = self.children.cast(Entity).filter(content_type=_ct)
        _count = schemata.count()
        return None if not _count else schemata.get() if (_count < 2) else schemata.filter(field_name=key).get()
    
    def get_subclass_entity(self, cls):
        """
        Return the child Entity matching the specified class or itself if not found. 
        """
        if not isinstance(cls, ModelBase) :
            return self
        _ct_sub = ContentType.objects.get_for_model(cls)
        children = self.children.cast(Entity).filter(content_type=_ct_sub)
        return children.get() if children.count() else self
    
#    def get_parent_entity(self, cls):
#        """Return the parent Entity matching the specified class."""
#        entity = self
#        _cls = entity.content_type.model_class() 
#        #first loop to detect schema relative to the same class
#        while isinstance(entity, Entity) and (cls != _cls) and not issubclass(cls, _cls) :
#            entity = entity.parent.cast()
#        assert isinstance(entity, Entity), "entity %s" % (entity)  
#        return entity

class Field(models.Model): #future name : ModelField
    """Define fields or properties of a class that will be displayed in the editor."""
    identifier = models.CharField(max_length=300)
    verbose_name = models.CharField(max_length=500)
    subfields = models.ManyToManyField('self', symmetrical=False, through='FieldGroup')
    
    @property
    def is_property(self):
        return bool(self.verbose_name)
    
    @property
    def is_grouper(self):
        return bool(self.subfields.count())
    
    class Meta :
        ordering = ['id']
        
    def __unicode__(self):
        return "%s" % (self.identifier)

achoices = (('A', 'add'), ('M', 'modify'), ('D', 'delete'), ('L', 'link'), ('U', 'unlink'), ('T', 'tag'), ('N', 'none'))
class Action(models.Model):
    """Action that could be done by a user."""
    name = models.CharField(primary_key=True, max_length=1, choices=achoices)
    
    class Meta :
        ordering = ['name']
    
    def __unicode__(self):
        return self.get_name_display()

ochoices = (('A', 'ascending'), ('D', 'descending'))
class Constraint(Cast): #future name : ModelDisplayConstraint
    """Display constraints."""
    entity = models.ForeignKey(Entity, related_name="constraints")
    form = models.CharField(max_length=256)
    form_style = models.CharField(max_length=50, null=True, blank=True)
    displayed_in_navigator = models.BooleanField(default=True)
    actions = models.ManyToManyField(Action)
    #display constraints
    shunt = models.BooleanField(default=False, help_text="tell if properties of an object will be displayed")
    hierarchy = models.BooleanField(default=False, help_text="display self referencing classes in a hierarchical view, i.e. only root nodes of the hierarchy will be displayed on the first level.")
    max_objects = models.PositiveIntegerField(null=True, blank=True, help_text="limit the number of objects linked to another by a reverse or local many to many field.")
    in_expansion = models.ManyToManyField(Field, through='InExpansion', related_name="is_in_expansion_of", help_text="tell which fields will detail an object")
    #subclass constraints
    display_subclasses = models.BooleanField(default=False)
    excluded_subclasses = models.ManyToManyField(ContentType, related_name="is_excluded_subclass_of")
    display_base_class = models.BooleanField(default=False)
#    limit_to_one_subclass = models.NullBooleanField()
    #display_base_class_only = models.NullBooleanField()
    #permissions and annotations
#    display_permissions = models.BooleanField(default=False, null=False, blank=False)
#    display_tags = models.BooleanField(default=False, null=False, blank=False)
#    display_annotations = models.BooleanField(default=False, null=False, blank=False)
#    display_attachments = models.BooleanField(default=False, null=False, blank=False)

    def __unicode__(self):
        return "%s : %s" % (self.__class__._meta.verbose_name, self.pk)

class InExpansion(models.Model):
    """
    List fields detailing a model class instance.
    """
    constraint = models.ForeignKey(Constraint)
    field = models.ForeignKey(Field)

class TableConstraint(Constraint): #future name : ModelDisplayAsTableConstraint
    in_header = models.ManyToManyField(Field, through='InHeader', related_name="is_in_header_of")
    pagination = models.PositiveSmallIntegerField(default=50)
    width = models.CharField(max_length=10, null=True, blank=True)

class InHeader(models.Model):
    """
    List fields detailing a model class instance
    and displayed in the header of the table representing this instance.  
    """
    tableconstraint = models.ForeignKey(TableConstraint)
    field = models.ForeignKey(Field)

class FieldGroup(models.Model):
    """
    Group fields contained in the header of a table.
    """
    field = models.ForeignKey(Field, related_name="is_grouper_of")
    subfield = models.ForeignKey(Field, related_name="is_grouped_in")
