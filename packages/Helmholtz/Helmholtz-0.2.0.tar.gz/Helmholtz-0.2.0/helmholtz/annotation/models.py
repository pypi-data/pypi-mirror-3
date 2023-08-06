#encoding:utf-8
from django.db import models
from helmholtz.core.models import Cast, CastManager, ObjectIndex
from helmholtz.units.fields import PhysicalQuantityField

"""
This module contains models useful to describe database objects
in a more explicit way with tags, annotations or attachments. 
"""

class BaseTagManager(CastManager):
    """Manage :class:`Tag` objects."""
    
    def apply(self, tags, objects):
        """Apply several :class:`Tag` instances to a set of objects."""
        index = ObjectIndex.objects.register_objects(objects)
        for tag in tags :
            tag.add(*index)
    
    def applied_on(self, tag):
        """
        Return objects on which the specified 
        the :class:`Tag` instance is applied on.
        """ 
        return tag.applied_on()

class TagManager(BaseTagManager):
    """Manage :class:`Tag` objects."""
    
    def apply(self, tags, objects):
        """Apply a set of :class:`Tag` instances to a set of objects."""
        annotations = [k for k in tags if k.__class__.__name__ == 'Tag']
        super(AnnotationManager, self).apply(annotations, objects)
    
    def tags(self, obj):
        """Return :class:`Tag` instances relative to the specified object."""
        index = ObjectIndex.objects.get_registered_object(obj)
        return index.tag_set.cast(Tag) if not index is None else Tag.objects.none()
    
    def annotations(self, obj):
        """Return :class:`Annotation` instances relative to the specified object."""
        return Annotation.objects.annotations(obj)
    
    def attachments(self, obj):
        """Return :class:`Attachment` instances relative to the specified object."""
        return Attachment.objects.attachments(obj)

class Tag(Cast):
    """
    Base class of all classes needed to annotate an object :
    
    ``label`` : identifier of the annotation.
    
    ``ìndices`` : a many to many field to object indices on which the annotation is applied.
    
    ``objects`` : the manager handling the kind of annotations. 
    """
    label = models.CharField(max_length=300)
    indices = models.ManyToManyField(ObjectIndex)
    
    objects = TagManager()
    
    def __unicode__(self):
        return self.label
    
    def apply(self, *objects):
        """Apply a the :class:`Tag` instance to a set of objects."""
        index = ObjectIndex.objects.register_objects(objects)
        self.add(index)
    
    def applied_on(self):
        """Return the set of objects on which the :class:`Tag` instance is applied."""
        return [k.object for k in self.indices.all()]

class AnnotationManager(BaseTagManager):
    """Manage :class:`Annotation` instances relative to an object."""
    
    def apply(self, tags, objects):
        """Apply :class:`Annotation` instances to a set of objects."""
        annotations = [k for k in tags if isinstance(k, Annotation)]
        super(AnnotationManager, self).apply(annotations, objects)

    def annotations(self, obj):
        """Return :class:`Annotation` instances relative to the specified object."""
        index = ObjectIndex.objects.get_registered_object(obj)
        return index.tag_set.cast(Annotation) if not index is None else Annotation.objects.none()

class Annotation(Tag):
    """
    Annotate an object with some text :
    
    ``text`` : description of the tag in order to make it more explicit.
    """
    text = models.TextField()
    
    objects = AnnotationManager()
    
    def __unicode__(self):
        return u"%s : %s ..." % (self.label, self.text[0:30])

class AttachmentManager(BaseTagManager):
    """Manage :class:`Attachment` instances relative to an object."""
    
    def apply(self, tags, objects):
        """Apply a set of :class:`Attachment` instances to a set of objects."""
        attachments = [k for k in tags if isinstance(k, Attachment)]
        super(AttachmentManager, self).apply(attachments, objects)
    
    def attachments(self, obj):
        """Return :class:`Attachment` instances relative to the specified object."""
        index = ObjectIndex.objects.get_registered_object(obj)
        return index.tag_set.cast(Attachment) if not index is None else Annotation.objects.none()

class Attachment(Tag):
    """
    Attach a document to an object. Give the ability
    to describe an object with a set of documents :
    
    ```document`` : the file to attach to an object.
    """
    document = models.FileField(upload_to="uploads/documents")
    
    objects = AttachmentManager()
    
    def __unicode__(self):
        return u"%s : %s" % (self.label, self.document)

class Descriptor(models.Model):
    """
    Extend properties of an object :
    
    ``name`` : the identifier of the descriptor.
    
    ``human_readable`` : a more explicit way to define the descriptor.
    """
    name = models.CharField(max_length=45)
    human_readable = models.TextField(null=True)
    
    def __unicode__(self):
        st = self.name
        if self.human_readable :
            st += " : %s" % self.human_readable
        return self.name

class StaticDescription(models.Model):
    """
    Assign a value to a :class:`Descriptor` :
    
    ``descriptor`` : the descriptor on which a value will be assigned.
    
    ``value`` : the value to assign to the descriptor.
    
    ``notes`` : notes concerning the affectation. 
    """
    descriptor = models.ForeignKey(Descriptor)
    value = PhysicalQuantityField(unit='');
    notes = models.TextField(null=True, blank=True)
