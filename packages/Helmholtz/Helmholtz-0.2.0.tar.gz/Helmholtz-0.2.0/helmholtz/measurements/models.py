#encoding:utf-8
import re
from django.core.exceptions import ValidationError
from django.db.models.base import ModelBase
from django.db import models
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes import generic
from helmholtz.core.models import Cast
from helmholtz.units.models import Unit

def is_range(value):
    regexp = "^(\[|\])\-{0,1}\d+(\.\d+){0,1}:\-{0,1}\d+(\.\d+){0,1}:\-{0,1}\d+(\.\d+){0,1}(\]|\[)$"
    match = re.match(regexp, value, re.UNICODE)
    if match :
        return True
    else :
        return False

def get_start_end_step(range):
    "Return start, end and step of the specified range"
    interval = range[1:-1].split(':')
    return interval[0], interval[2], interval[1]

def get_evaluations(start, end, step, tp=float):
    return tp(start), tp(end), tp(step)

def verify_pattern(pattern):
    """Verify if the specified pattern is correctly defined."""
    regexp = "^(((\[|\])\-{0,1}\d+(\.\d+){0,1}:\-{0,1}\d+(\.\d+){0,1}:\-{0,1}\d+(\.\d+){0,1}(\[|\]))|\w+|\w+(\.\w+)|(\-{0,1}\d+(\.\d+)))((\|(((\[|\])\-{0,1}\d+(\.\d+){0,1}:\-{0,1}\d+(\.\d+){0,1}:\-{0,1}\d+(\.\d+){0,1}(\[|\]))|\w+|(\-{0,1}\d+(\.\d+))))*)$"
    match = re.match(regexp, pattern, re.UNICODE)
    if not match :
        raise ValidationError("bad pattern format")   
    else :
        n = 1
        for single_pattern in pattern.split('|') :
            if is_range(single_pattern) :
                start, end, step = get_start_end_step(single_pattern)
                f_start, f_end, f_step = get_evaluations(start, end, step)
                #as pattern is a range, step cannot be zero
                if not (f_step < 0 or f_step > 0) :
                    raise ValidationError("bad range format, step value of pattern number %s cannot be zero" % n) 
                #verify that lower and upper bound are coherent with the specified step
                if ((f_step >= 0) and (f_start > f_end)) or ((f_step < 0) and (f_end > f_start)) :
                    raise ValidationError("bad range format, pattern number %s would be [%s:%s:%s]" % (n, end, step, start))
                n += 1
                    
choices = (('I', 'integer'), ('F', 'float'), ('S', 'string'), ('B', 'boolean'), ('M', 'model'))
class Parameter(models.Model):
    """Extend base properties of a class."""
    content_type = models.ForeignKey(ContentType)
    label = models.CharField(max_length=50)
    verbose_name = models.TextField(null=True, blank=True)
    pattern = models.TextField(null=True, blank=True, help_text="constraints a measure to a set of values defined like this : [first1:step1:last1]|[first2:step2:last2] or text1|text2|text3")
    type = models.CharField(max_length=1, choices=choices)
    unit = models.ForeignKey(Unit, null=True, blank=True)
    notes = models.TextField(null=True, blank=True)
    
    @property
    def is_constrained(self):
        """Tell if the value of a parameter is constrained by a pattern."""
        return bool(self.pattern)
    
    def get_type(self):
        """Get the Python type corresponding to the Parameter type."""
        dct = {
            'I':int,
            'F':float,
            'S':unicode,
            'B':bool,
            'M':ModelBase
        }
        return dct[self.type]

    def get_subclass(self):
        dct = {
            'I':IntegerMeasurement,
            'F':FloatMeasurement,
            'S':StringMeasurement,
            'B':BoolMeasurement
        }
        return dct[self.type]
    
    def clean(self):
        tp = self.get_type()
        if self.pattern :
            if (tp != ModelBase) :
                self.get_values()
            else :
                try :
                    split = self.pattern.split('.')
                    content_type = ContentType.objects.get(app_label__iexact=split[0], model__iexact=split[1])
                except :
                    raise ValidationError("model %s not in database model." % self.pattern)
        elif (tp == ModelBase) :
            raise ValidationError("pattern cannot be null if type is ModelBase")
    
    def get_range_values(self, range, tp):
        """Get values corresponding to the specified range."""
        values = list()
        
        #get start, end and step values as a list of float
        start, end, step = get_start_end_step(range)
        f_start, f_end, f_step = get_evaluations(start, end, step, float)
        
        #compute the visible range from the pattern
        val = f_start
        while ((f_step > 0) and (val <= (f_end + f_step))) or ((f_step < 0) and (val >= (f_end + f_step))) :
            #avoid displaying 0.0 in a weird way
            #by fixing a precision factor
            precision = len(str(f_step).split('.')[1])
            values.append(round(val, precision))
            val += f_step
        
        #exclude the first element if the pattern starts with ']'
        if range.startswith(']') :
            values = values[1:]
        
        #exclude the last element if the pattern ends with '['
        if range.endswith('[') :
            values = values[:-1]
        
        #finally convert to specified type
        return [tp(k) for k in values]
    
    def get_values(self):
        """Get values corresponding to the specified pattern."""
        if self.pattern and (self.get_type() != ModelBase) :
            tp = self.get_type()
            
            #compute all values corresponding to the pattern
            values = list()
            str_values = self.pattern.split('|') 
            n = 1
            for str in str_values :
                if is_range(str) :
                    values.extend(self.get_range_values(str, tp))
                else :
                    #show the incompatibility between 
                    #a single string pattern and the specified object type
                    try :
                        values.append(tp(str))
                    except :
                        raise ValidationError("bad pattern format, pattern %s '%s' is not '%s'" % (n, str, tp.__name__))
            
            #avoid redundancies with a set
            lst = list(set(values))
            lst.sort()
            return lst
        
        elif (self.get_type() == ModelBase) :
            split = self.pattern.split('.')
            content_type = ContentType.objects.get(app_label__iexact=split[0], model__iexact=split[1])
            values = content_type.model_class().objects.all()
            return values
        else :
            return None
    
    def __unicode__(self):
        return self.label

class GenericMeasurement(Cast):
    """
    Base class of all kind of measurements. Subclasses set the value and unit 
    of additional parameters defined into the Parameter class.
    """
    parameter = models.ForeignKey(Parameter)
    unit = models.ForeignKey(Unit, null=True, blank=True)
    timestamp = models.DateTimeField(null=True, blank=True)
    content_type = models.ForeignKey(ContentType, null=True, blank=True)
    object_id = models.PositiveIntegerField(null=True, blank=True)
    object = generic.GenericForeignKey('content_type', 'object_id')
    
    def get_unit(self):
        return self.unit if self.unit else (self.parameter.unit if self.parameter.unit else None)
    
    def get_symbol(self):
        return self.get_unit().symbol if self.unit else None
    symbol = property(get_symbol)        
    
    def __unicode__(self):
        measurement = self.cast()
        if hasattr(measurement, 'value') :
            return "%s:%s %s at %s on object %s" % (self.parameter.label, measurement.value, self.unit, self.timestamp, self.object)
        else :
            return "%s in %s at %s on object %s" % (self.parameter.label, self.unit, self.timestamp, self.object)

class BoolMeasurement(GenericMeasurement):
    value = models.BooleanField()

class IntegerMeasurement(GenericMeasurement):
    value = models.IntegerField()

class FloatMeasurement(GenericMeasurement):
    value = models.FloatField()

class StringMeasurement(GenericMeasurement):
    value = models.TextField()

#experimental classes

class ModelReference_Integer(GenericMeasurement):
    value = generic.GenericForeignKey('c_type', 'o_id')
    c_type = models.ForeignKey(ContentType, null=True, blank=True)
    o_id = models.PositiveIntegerField(null=True, blank=True)
    
class ModelReference_String(GenericMeasurement):
    value = generic.GenericForeignKey('c_type', 'o_id')
    c_type = models.ForeignKey(ContentType, null=True, blank=True)
    o_id = models.TextField(null=True, blank=True)
