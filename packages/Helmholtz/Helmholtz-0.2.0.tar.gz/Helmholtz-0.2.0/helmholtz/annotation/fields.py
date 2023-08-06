from django.core.exceptions import ValidationError
from django.db import models
from django import forms

class Quality(object):
    """
    A python object returned when a :class:``QualityField`
    instance is accessed from an object.
    """
    
    def __init__(self, value, max):
        self.max = int(max)
        self.value = int(value)
         
    def __str__(self):
        return '%s/%s' % (self.value, self.max)
    
    def __unicode__(self):
        return u'%s/%s' % (self.value, self.max)
    
    def __repr__(self):
        return "Quality(%s,%s)" % (self.value, self.max) 
    
    def db_repr(self):
        return """%s""" % self.value

class QualityField(models.TextField):
    """
    A subclass of :class:`TextField` useful to
    store quality annotation in database.
    """
    __metaclass__ = models.SubfieldBase
    
    def __init__(self, max=5, *args, **kwargs):
        self.max = max
        help_text = "Specify a value from 0 to %s." % max
        super(QualityField, self).__init__(help_text=help_text, *args, **kwargs)
    
    def validate(self, value, model_instance):
        if not (value is None or isinstance(value, Quality)) :
            raise ValidationError('quality value must be a Quality object')
        if value.value > self.max :
            raise ValidationError('quality value must be inferior or equal to %s' % self.max)
    
    def to_python(self, value):
        if isinstance(value, Quality) or value is None :
            return value
        #see if there are not any integrity errors
        #between the python model and database data
        try :
            val, max = [int(k) for k in value.split('/')]
        except :
            raise Exception('bad database format')
        assert max == self.max, "max from the database side is not equal to max defined in the python model : %s != %s" % (self.max, max)
        return Quality(val, self.max)
    
    def get_prep_value(self, value):
        return value.db_repr() if value else None
    
    def formfield(self, **kwargs): 
        return QualityFormField(max=self.max, help_text=self.help_text, **kwargs)

class QualityFormField(forms.CharField):
    """
    A subclass of :class:`CharField` creating a :class:`Quality`
    instance from the user inputs.
    """
    
    def __init__(self, max, **kwargs):
        self.max = max
        kwargs['help_text'] = "please enter a number that is inferior or equal to %s" % self.max
        super(QualityFormField, self).__init__(**kwargs)
    
    def prepare_value(self, data):
        if isinstance(data, Quality) :
            return data.value
        else :
            return data
    
    def to_python(self, value):
        if not value :
            if not self.required :
                return None
            else :
                raise ValidationError('please specify quality value')
        else :
            try :
                val = int(value)
            except :
                raise ValidationError('quality must an integer')
            return Quality(val, self.max)
