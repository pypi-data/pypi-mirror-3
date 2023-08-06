#encoding:utf-8

#Here's some usecases :
# 1 - define a laboratory, its hierarchical organization, specificities and research axes
# 2 - store information useful to contact people or their relative laboratory to ask more explanations concerning experiments 
# 3 - set the list of people that have been hired by a laboratory and that have collaborated on experiments
# 4 - track in time someone's position
# 5 - define more accurately the profile of a user
from datetime import date
from django.db import models
from django.db.models import Count
from django.contrib.auth.models import Group, User
from helmholtz.core.models import Cast, HierarchicalStructure
from helmholtz.core.shortcuts import get_class, get_subclasses
from helmholtz.people.fields import PhoneNumberField

class Contact(Cast):
    """
    Base class of all type of contacts like
    :class:`Address`, :class:`Phone`, :class:`Fax`,
    :class:`E-mail` or :class:`Website` :
    
    ``label`` : the label identifying the contact.
    """
    label = models.CharField(max_length=100)
    
    def __unicode__(self):
        return self.label
    
    def cast_keys(self):
        keys = [k.__name__.lower() for k in get_subclasses(self.__class__)]
        return keys
    
    class Meta :
        ordering = ['label']

class Address(Contact):
    """A subclass of :class:`Contact` to store addresses."""
    street_address_1 = models.CharField(max_length=256, verbose_name="address 1")
    street_address_2 = models.CharField(max_length=256, null=True, blank=True, verbose_name="address 2")
    postal_code = models.CharField(max_length=10)
    town = models.CharField(max_length=256)
    state = models.CharField(max_length=256, null=True, blank=True)
    country = models.CharField(max_length=256)
    
    def __unicode__(self):
        st = "%s : %s " % (self.label, self.street_address_1)
        if self.street_address_2 :
            st += "%s " % (self.street_address_2)
        st += "%s %s %s" % (self.postal_code, self.town, self.country)
        if self.state :
            st += " (%s)" % self.state
        return st  
    
    class Meta:
        ordering = ['label']
        verbose_name_plural = "addresses"

class EMail(Contact):
    """A subclass of :class:`Contact` to store email addresses."""
    identifier = models.EmailField(verbose_name="address", max_length=256)
    
    def __unicode__(self):
        st = "%s : %s" % (self.label, self.identifier)
        return st
    
    class Meta:
        verbose_name = "e-mail"

class Phone(Contact):
    """A subclass of :class:`Contact` to store phone numbers."""
    identifier = PhoneNumberField(verbose_name="number", max_length=16)
    
    def __unicode__(self):
        st = "%s : %s" % (self.label, self.identifier)
        return st

class Fax(Contact):
    """A subclass of :class:`Contact` to store fax numbers."""
    identifier = PhoneNumberField(verbose_name="number", max_length=16)
    
    def __unicode__(self):
        st = "%s : %s" % (self.label, self.identifier)
        return st
    
    class Meta:
        verbose_name_plural = "faxes"

class WebSite(Contact):
    """A subclass of :class:`Contact` to store websites."""
    identifier = models.URLField(verbose_name="url", verify_exists=False)
    
    def __unicode__(self):
        st = "%s : %s" % (self.label, self.identifier)
        return st
    
    class Meta:
        verbose_name = "website"

class SkillType(models.Model):
    """
    ScientificStructure's or People's scientific or technical skills.
    """
    name = models.CharField(max_length=300, primary_key=True)
    parent = models.ForeignKey('self', null=True, blank=True)

    def __unicode__(self):
        return u"%s" % (self.name)
    
    class Meta:
        ordering = ['name', 'parent__name']

class ScientificStructure(HierarchicalStructure):
    """Hierarchical structure representing a large variety of scientific structures.
    
    NB : The db_group parameter specifies the group relative to a scientific structure. 
    Consequently, it is possible to implement a hierarchical user administration.
    """
    diminutive = models.CharField(max_length=32) # should be called "shortname" or something. Not all structures have acronyms
    name = models.CharField(max_length=256)
    logo = models.ImageField(upload_to="uploads/images/logos", null=True, blank=True)
    parent = models.ForeignKey('self', null=True, blank=True)
    is_data_provider = models.BooleanField(default=False, null=False, blank=False)
    foundation_date = models.DateField(null=True, blank=True)
    dissolution_date = models.DateField(null=True, blank=True)
    description = models.TextField(null=True, blank=True)
    contacts = models.ManyToManyField(Contact, null=True, blank=True)
    db_group = models.OneToOneField(Group, verbose_name="database group", null=True, blank=True)
    #skills = models.ManyToManyField(SkillType)
    
    class Meta :
        ordering = ['name']
    
    def __unicode__(self, separator=u" \u2192 "):
        complete_path = self.diminutive or self.name
        if self.parent:
            complete_path = u"%s%s%s" % (self.parent.__unicode__(separator=separator), separator, complete_path)
        return complete_path
    
    @property
    def manager(self):
        """Return the manager a of the :class:`ScientificStructure` instance."""
        positions = self.position_set.filter(position_type__name="manager")
        return positions.latest('start').researcher if positions else None
    
    def _years(self):
        """Age of the :class:`ScientificStructure` instance in years."""
        today = date.today()
        _end = self.dissolution_date or today
        if self.foundation_date :
            return int(round((_end - self.foundation_date).days / 365.25))
        else:
            return None
    years = property(_years)
    
    def get_main_and_sub_structures(self):
        _main = self.get_root()
        _sub = self if (_main != self) else None
        return _main, _sub
    
    def create_diminutive(self, separator="_"):
        """
        Return an auto generated diminutive from the
        name of the :class:`ScientificStructure` instance.
        """
        if not self.diminutive:
            self.diminutive = self.name.replace(" ", separator)
    
    @property
    def researchers(self):
        """
        Return :class:`django.contrib.auth.models.Researchers`
        instances corresponding to the :class:`ScientificStructure`
        instance and its children.
        """
        structures = list()
        structures.append(self)
        structures.extend(self.get_children(True, False))
        researchers = Researcher.objects.filter(position__structure__in=structures).order_by('position__position_type__rank', 'last_name', 'first_name').distinct()
        return researchers
    
    @property
    def structures(self):
        return self.get_children(True, True)
    
    @property
    def experiments(self):
        """
        Return :class:`Experiment` instances provided
        by the :class:`ScientificStructure` instance.
        """
        q1 = models.Q(setup__place__parent=self)
        q2 = models.Q(setup__place=self)
        cls = get_class('experiment', 'Experiment')
        return cls.objects.filter(q1 | q2).distinct()
    
    def number_of_researchers(self):
        """
        Get the number of :class:`Researcher` instances
        working in the :class:`ScientificStructure` instance.
        """
        aggregate = self.position_set.all().aggregate(Count("researcher", distinct=True))
        count = aggregate["researcher__count"]
        if self.scientificstructure_set.count :
            for children in self.get_children(recursive=False) :
                count += children.number_of_researchers()
        return count
    
    def get_groups(self, recursive=False):
        """
        Return :class:`django.contrib.auth.models.Group`
        instances corresponding to the :class:`ScientificStructure`
        instance and its children.
        """
        groups = list()
        groups.append(self.db_group.name)
        if recursive :
            groups = [k.db_group.name for k in self.get_children(recursive)]
        return Group.objects.filter(name__in=groups)
    
    def emails(self):
        """
        Return :class:`EMail` instances
        corresponding to the :class:`ScientificStructure`
        instance and its children.
        """
        return self.contacts.cast(EMail)
    
    def addresses(self):
        """
        Return :class:`Address` instances
        corresponding to the :class:`ScientificStructure`
        instance and its children.
        """
        return self.contacts.cast(Address)
    
    def phones(self):
        """
        Return :class:`Phone` instances
        corresponding to the :class:`ScientificStructure`
        instance and its children.
        """
        return self.contacts.cast(Phone)
    
    def faxes(self):
        """
        Return :class:`Fax` instances
        corresponding to the :class:`ScientificStructure`
        instance and its children.
        """
        return self.contacts.cast(Fax)
    
    def websites(self):
        """
        Return :class:`WebSite` instances
        corresponding to the :class:`ScientificStructure`
        instance and its children.
        """
        return self.contacts.cast(WebSite)

class StructureSkill(models.Model):
    """
    List :class:`ScientificStructure` skills to order them by priority.
    """
    structure = models.ForeignKey(ScientificStructure)
    skill = models.ForeignKey(SkillType)
    priority = models.PositiveSmallIntegerField()
    
class Researcher(models.Model):
    """
    Anybody working in a :class:`ScientificStructure`.
    Used as a profile for a database :class:`django.contrib.auth.models.User`.
    """
    first_name = models.CharField(max_length=30)
    last_name = models.CharField(max_length=30)
    photo = models.ImageField(upload_to="uploads/images/photos", null=True, blank=True)
    user = models.OneToOneField(User, null=True, blank=True, verbose_name="database user")#duplication because an employee isn't necessary a database user
    contacts = models.ManyToManyField(Contact, null=True, blank=True)
    notes = models.TextField(null=True, blank=True)
    
    def __unicode__(self):
        return self.get_full_name()
    
    def get_full_name(self):
        """
        Get the full name of the :class:`Researcher` instance, 
        i.e. the combination between its first and last names.
        """
        return "%s %s" % (self.first_name, self.last_name)
    
    def position_in_structure(self, structure):
        """
        Return the latest :class:`Position` of the 
        :class:`Researcher` instance for the specified
        :class:`ScientificStructure`.
        """
        structures = list()
        structures.append(structure)
        structures.extend(structure.get_children(True, False))
        positions = self.position_set.filter(structure__in=structures)
        position = positions.latest('start') if positions else None
        return position
    
    def current_position(self):
        """
        Return the current :class:`Position` of the 
        :class:`Researcher` instance.
        """
        today = date.today()
        last_position = self.last_position()
        if last_position :
            if not last_position.end or ((last_position.start <= today) and (last_position.end >= today)) :
                return last_position
        return None
    
    def last_position(self, structure=None):
        """
        Return the last effective :class:`Position` of
        the :class:`Researcher` instance in the specified
        :class:`ScientificStructure`.
        """
        if structure :
            structures = list()
            structures.append(structure)
            structures.extend(structure.get_children(True, False))
            positions = self.position_set.filter(structure__in=structures)
        else :
            positions = self.position_set.all()
        return positions.latest("start") if positions else None
    
    def number_of_structures(self):
        """
        Get the number of :class:`ScientificStructure`
        where a :class:`Researcher` has worked.
        """
        aggregate = self.position_set.all().aggregate(Count("structure", distinct=True))
        return aggregate["structure__count"]
    
    def emails(self):
        """
        Return :class:`EMail` instances corresponding
        to the :class:`Researcher` instance.
        """
        return self.contacts.cast(EMail)
    
    def addresses(self):
        """
        Return :class:`Address` instances corresponding
        to the :class:`Researcher` instance.
        """
        return self.contacts.cast(Address)
    
    def phones(self):
        """
        Return :class:`Phone` instances corresponding
        to the :class:`Researcher` instance.
        """
        return self.contacts.cast(Phone)
    
    def faxes(self):
        """
        Return :class:`Fax` instances corresponding
        to the :class:`Researcher` instance.
        """
        return self.contacts.cast(Fax)
    
    def websites(self):
        """
        Return :class:`WebSite` instances corresponding
        to the :class:`Researcher` instance.
        """
        return self.contacts.cast(WebSite)
    
    class Meta:
        ordering = ['last_name', 'first_name']

class PositionType(models.Model):
    """Type of 'contract' useful to define someone's :class:`Position`."""
    name = models.CharField(primary_key=True, max_length=250)
    rank = models.PositiveSmallIntegerField(null=True)
    
    def __unicode__(self):
        return u"%s" % (self.name)
    
    class Meta:
        ordering = ['rank', 'name']

class Position(models.Model):
    """
    Contract linking a :class:`Researcher` to a :class:`ScientificStructure`.
    
    NB : this class brings more flexibility by separating people 
    descriptions from their positions in a hierarchical structure.
    """
    researcher = models.ForeignKey(Researcher)
    structure = models.ForeignKey(ScientificStructure)
    position_type = models.ForeignKey(PositionType)
    start = models.DateField()
    end = models.DateField(null=True)
    notes = models.TextField(null=True, blank=True)
     
    class Meta:
        ordering = ['-start', 'structure', 'researcher']
        
    def __unicode__(self):
        end = self.end or "present"
        st = u"%s, %s in %s from %s to %s" % (self.researcher, self.position_type, self.structure, self.start, end)
        return st

class Supplier(models.Model):
    """Supplier of resources used in a laboratory."""
    name = models.CharField(max_length=250, primary_key=True)
    contacts = models.ManyToManyField(Contact, blank=True)
    
    def __unicode__(self):
        return self.name
    
    class Meta:
        ordering = ['name']
