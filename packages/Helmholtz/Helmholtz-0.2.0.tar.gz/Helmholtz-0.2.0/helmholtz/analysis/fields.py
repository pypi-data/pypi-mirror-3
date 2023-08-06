#encoding:utf-8
from django.db import models
try:
    import cPickle as pickle
except ImportError:
    import pickle

class PickledObjectField(models.Field):
    __metaclass__ = models.SubfieldBase
    
    def to_python(self, value):
        try :
            return pickle.loads(str(value))
        except :
            return value
    
    def get_db_prep_save(self, value, connection):
        return pickle.dumps(value)
    
    def get_internal_type(self): 
        return 'TextField'
    
    def get_db_prep_lookup(self, lookup_type, value, connection, prepared=False):
        if lookup_type == 'exact':
            value = self.get_db_prep_save(value, connection)
            return super(PickledObjectField, self).get_db_prep_lookup(lookup_type, value, connection, prepared=False)
        elif lookup_type == 'in':
            value = [self.get_db_prep_save(v, connection) for v in value]
            return super(PickledObjectField, self).get_db_prep_lookup(lookup_type, value, connection, prepared=False)
        else:
            raise TypeError('Lookup type %s is not supported.' % lookup_type)
