#encoding:utf-8
from django.db import models
from numpy import array, ndarray

class Matrix(object):
    """
    A class to be able to represent multidimensional data as a Python object. 
    """
    def __init__(self, data):
        self.data = data if isinstance(data, ndarray) else array(data)
        self.shape = self.data.shape
        self.ndim = self.data.ndim
    
    def __str__(self):
        return self.data.__str__()
    
    def __unicode__(self):
        return u"%s" % self.__str__()
    
    def __repr__(self):
        return "Matrix(%s)" % (self.data.__repr__())
    
    def db_repr(self, data=None, starting_point=True):
        if starting_point :
            data = self.data 
            
        st = '{'
        for item in data :
            if isinstance(item, ndarray) :
                substr = self.db_repr(item, False)
            else :
                substr = item
            st += substr 
            if item != data[-1] :
                st += ','   
        st += '}'
        
        return st

class MatrixField(models.Field):
    """
    A field to be able to store multidimensional data.
    """
    __metaclass__ = models.SubfieldBase
    
    def __init__(self, native_type='integer', dimensions=[None], *args, **kwargs):
        self.dimensions = dimensions
        self.native_types = ['integer', 'numeric', 'float', 'test', 'varchar', 'double precision']
        if native_type in self.native_types :
            self.native_type = native_type
        else :
            raise Exception('native type not supported')
        super(MatrixField, self).__init__(*args, **kwargs)
    
    def db_type(self, connection):
        st = self.native_type
        for dimension in self.dimensions :
            st += "[%s]" % dimension if dimension else '[]'
        return st
    
    def get_prep_lookup(self, lookup_type, value):
        # We only handle 'exact' and 'in'. All others are errors.
        if lookup_type == 'exact':
            return self.get_prep_value(value)
        elif lookup_type == 'in':
            return [self.get_prep_value(v) for v in value]
        else:
            raise TypeError('Lookup type %r not supported.' % lookup_type)
    
    def get_prep_value(self, value):
        return value.db_repr() if value else None
    
    def to_python(self, value):
        if isinstance(value, Matrix) :
            return value
        if value :       
            return Matrix(array(value))
        else :
            return value
