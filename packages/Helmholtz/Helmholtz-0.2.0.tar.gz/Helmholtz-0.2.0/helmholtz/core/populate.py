#encoding:utf-8
from pprint import pprint
from copy import deepcopy
from django.conf import settings
from django.utils.datastructures import SortedDict
from django.db.models import Model, ForeignKey
from django.db.models.loading import get_models
from django.core.management.base import NoArgsCommand
from django.contrib.auth.models import Group, User
from django.contrib.contenttypes.models import ContentType
from helmholtz.core.schema import get_all_fields, foreign_keys, many_to_many_fields, reverse_one_to_one_keys, reverse_foreign_keys, reverse_many_to_many_fields, generic_foreign_keys, generic_relations, subclasses
from helmholtz.access_control.models import Permission
from helmholtz.core.loggers import default_logger

"""
This module provides a way to populate the 
database from a dictionary specified set of data.
"""

logging = default_logger(__name__)
keywords = ['__cleanup__']#force and __target_class__ are reserved

def list_or_set_recursion(entry_point, cleanup, recursive):
    index = 0
    to_clean = []
    for item in entry_point :
        if isinstance(item, Column) :
            entry_point[index] = item.dictionarize(cleanup, recursive, False)
            if not entry_point[index] :
                to_clean.append(index)
        elif recursive and isinstance(item, dict) :
            entry_point[index] = dictionarize(item, cleanup, recursive, False)
            if not entry_point[index] :
                to_clean.append(index)  
        elif item.__class__.__name__ == 'NoneType' :
            to_clean.append(index)  
        index += 1
        
    if cleanup :
        for index in to_clean :
            entry_point.pop(index)

def dictionarize(props, cleanup=False, recursive=True, starting_point=True):
    """Generate a dictionary from the object structure."""
    dct = props
    to_clean = []
    for attr in dct :
        if isinstance(dct[attr], Column) and recursive :
            dct[attr] = dct[attr].dictionarize(cleanup, recursive, False)
            if not dct[attr] :
                to_clean.append(attr)
        elif isinstance(dct[attr], dict) and recursive :
            dct[attr] = dictionarize(dct[attr], cleanup, recursive, False)
            if not dct[attr] :
                to_clean.append(attr)
        elif (isinstance(dct[attr], list) or isinstance(dct[attr], set)) :
            if (len(dct[attr]) > 0) :
                if recursive : 
                    list_or_set_recursion(dct[attr], cleanup, recursive)
            else :
                to_clean.append(attr)  
        elif (not dct[attr]) and not isinstance(dct[attr], bool) :
            dct[attr] = None
            to_clean.append(attr)
    if cleanup :
        for attr in to_clean :
            dct.pop(attr)       
    return dct

class Column(object):
    """
    A way to represent a hierachical structure 
    and provide the dot notation on each of its node.
    """
    def __init__(self, entry_point, recursive=True):
        self.__dict__['_sorted_dict'] = SortedDict()
        self.__dict__['entry_point'] = deepcopy(entry_point)
        self.objectify()
        self.__dict__.pop('entry_point')

    def __getattr__(self, name): 
        return self._sorted_dict[name]
    
    def __setattr__(self, name, value):
        self._sorted_dict[name] = value
    
    def __delattr__(self, name):
        if name in self._sorted_dict :
            del self._sorted_dict[name]
        else :
            super(Column, self).__delattr__(self, name)

    def __deepcopy__(self, memo):
        new = self.__class__({}, False)
        new._sorted_dict.update(deepcopy(self._sorted_dict))
        return new
#        new = self.__class__(deepcopy(self._sorted_dict), True)
#        return new  
        
    def objectify(self, recursive=True):
        """Generate the object tree from a dictionary."""
        for field in self.entry_point :
            entry_point = self.entry_point[field]
            if isinstance(entry_point, dict) and (len(entry_point) > 0) :
                new_object = Column(entry_point, recursive) 
                self._sorted_dict[field] = new_object
            else :
                self._sorted_dict[field] = entry_point 
                if (isinstance(entry_point, list) or isinstance(entry_point, set)) and (len(entry_point) > 0) :
                    for index, item in enumerate(entry_point) :
                        assert isinstance(item, (dict , int, float, bool, str, unicode, Column, Model)), 'not implemented case : %s' % item.__class__.__name__
                        if isinstance(item, dict) :
                            new_object = Column(item, recursive) 
                            entry_point[index] = new_object
    
    def list_or_set_recursion(self, entry_point, objects, cleanup, recursive):
        """Enable the recursion even for node containing list or set."""
        to_clean = []
        for index, item in enumerate(objects) :
            if isinstance(item, Column) :
                sub_cleanup = cleanup if not hasattr(item, '__cleanup__') else item.__cleanup__
                new_item = item.dictionarize(sub_cleanup, recursive, False)
                entry_point.append(new_item)
                if not new_item :
                    to_clean.append(index)
            elif isinstance(item, dict) :
                sub_cleanup = cleanup if not item.has_key('__cleanup__') else item['__cleanup__']
                new_item = dictionarize(item, sub_cleanup, recursive, False)
                entry_point.append(new_item)
                if not new_item :
                    to_clean.append(index)    
            elif recursive and (isinstance(item, list) or isinstance(item, set)) and (len(item) > 0) :
                new_item = self.list_or_set_recursion(entry_point[index], item, cleanup, recursive)
                entry_point.append(new_item)
                if not new_item :
                    to_clean.append(index)
            elif item.__class__.__name__ == 'NoneType' :
                entry_point.append(item)
                if not item :
                    to_clean.append(index)
            else :
                entry_point.append(item)        
        if cleanup :
            for index in to_clean :
                entry_point.pop(index)
    
    def dictionarize(self, cleanup=False, recursive=True, starting_point=True):
        """Return a dictionary from the object structure."""
        dct = SortedDict()
        to_clean = []
        for attr in self._sorted_dict :
            # to avoid recursion caused by a dictionary
            # force a dictionary to be a node of the object
            obj = self._sorted_dict[attr] 
#            if isinstance(obj, dict) and recursive :
#                self._sorted_dict[attr] = Column(obj)
#                obj = self._sorted_dict[attr] 
            
            if isinstance(obj, dict) and recursive :
                sub_cleanup = cleanup if not obj.has_key('__cleanup__') else obj['__cleanup__']
                dct[attr] = dictionarize(obj, sub_cleanup, recursive, False)
                if not dct[attr] :
                    to_clean.append(attr)
            elif isinstance(obj, Column) and recursive :
                sub_cleanup = cleanup if not hasattr(obj, '__cleanup__') else obj.__cleanup__
                dct[attr] = obj.dictionarize(sub_cleanup, recursive, False)
                if not dct[attr] :
                    to_clean.append(attr)
            elif (isinstance(obj, list) or isinstance(obj, set)) :
                dct[attr] = obj.__class__()
                if len(obj) > 0 : 
                    if recursive :  
                        self.list_or_set_recursion(dct[attr], obj, cleanup, recursive)    
                else :
                    to_clean.append(attr)
            elif obj.__class__.__name__ == 'NoneType' :#(not obj) and not isinstance(obj, bool) :
                dct[attr] = None
                to_clean.append(attr)
            elif not (attr in keywords) :
                dct[attr] = obj
                
        #cleanup nodes that are empty dictionaries
        if cleanup :
            for attr in to_clean :
                dct.pop(attr)    
        return dct            

class Populate(object):
    
    def __init__(self):
        self.all_classes = get_models() #get_application_classes()
    
    def cleanup_database(self, excluded_tables=[], excluded_apps=[]):
        """Cleanup all database tables excepting those where name appears in the exclude parameter and not included in applications."""
        if len(excluded_apps) < 1 :
            model_classes = [k for k in self.all_classes if not (k.__name__ in excluded_tables)]
        else :
            model_classes = [k for k in self.all_classes if (not (k.__name__ in excluded_tables)) and (not (k.__module__.split('.')[-1] in excluded_apps))]
        for cls in model_classes :
            cls.objects.all().delete()
    
    def transform(self, props, fks, generic_fks, entity):
        """Replaces field values by their corresponding objects."""
        global all_classes
        cache = props.copy()
        for property in cache :
            if (cache[property].__class__.__class__.__name__ != "ModelBase") : 
                pk_db = entity._meta.pk.name
#                if (property in fks) and (property != pk_db) :
                if (property in fks) and ((property != pk_db) or not issubclass(entity, entity._meta.pk.rel.to)) :
                    #get or create object corresponding to a foreign key that is not a super class pointer (*_ptr)
                    
                    tmp = cache[property]
                    if tmp :
                        attributes = [tmp]
                        entity = fks[property]['class'] 
                        #replace nested objects 
                        new_object = self.store(entity, attributes)[0]
                        cache[property] = new_object
                elif (property in generic_fks) :
                    #get or create object corresponding to a generic foreign key
                    tmp = cache[property]
                    if tmp :
                        try :
                            entity = tmp.pop('__target_class__')
                            entity = [k for k in self.all_classes if k.__name__ == entity][0]  
                        except :
                            raise Exception('as %s is a GenericForeignKey please specify the target type in the class field' % (property))  
                        attributes = [tmp] 
                        #replace nested objects 
                        new_object = self.store(entity, attributes)[0]
                        cache[property] = new_object
        return cache
    
    def reorder_from_sorteddict(self, dct1, dct2):
        pass
    
    def _introspect_model(self, entity):
        return foreign_keys(entity), generic_foreign_keys(entity), subclasses(entity), self._many_related_fields(entity)
    
    def _many_related_fields(self, entity):
        fields = SortedDict()
        fields.update(many_to_many_fields(entity))
        fields.update(reverse_one_to_one_keys(entity))
        fields.update(reverse_foreign_keys(entity))
        fields.update(reverse_many_to_many_fields(entity))
        fields.update(generic_relations(entity))
        return fields
    
    def _cleanup(self, starting_point, props):
        """Cleanup and convert to a dictionary provided data."""
        if starting_point :
            if isinstance(props, Column) :
                cleanup = True if not hasattr(props, '__cleanup__') else props.__cleanup__
                cleaned = props.dictionarize(cleanup=cleanup)
            elif isinstance(props, dict) :
                cleanup = True if not props.has_key('__cleanup__') else props['__cleanup__']
                cleaned = dictionarize(props, cleanup=cleanup)
        else :
            cleaned = props
        return cleaned
    
    def _reorder(self, properties, many_related_fields):
        """Reorder regarding property order."""
        result = SortedDict()
        for field in properties :
            if many_related_fields.has_key(field) :
                result[field] = many_related_fields[field]
        return result
    
    def _to_create(self, many_related_fields, props):
        """Get fields implying the creation of a new object."""
        to_create = SortedDict()
        for field in many_related_fields :
            if props.has_key(field) :
                to_create[field] = props.pop(field)
        return to_create
    
    def _delegate(self, subcls, props):
        """Get fields delegating the creation of a new object to a subclass."""
        delegate = dict()
        for field in subcls :
            if props.has_key(field) :
                delegate[field] = props.pop(field)
        assert len(delegate) < 2, "cannot derivate twice"
        return delegate
    
    def _attach_object(self, aggregate, to_create, new_object, connect_to_base, entity):
        """Create relations between objects."""
        for field in aggregate :
            if to_create.has_key(field) and to_create[field]:
                if aggregate[field]['type'] == 'm2m' :
                    manager = getattr(new_object, field)
                    m2m_entity = aggregate[field]['class']
                    if hasattr(manager, 'add') :
                        new_objects = self.store(m2m_entity, to_create[field], starting_point=False) 
                        manager.add(*new_objects)
                    else :
                        reverse_entity = manager.through
                        all_fields = get_all_fields(manager.through)
                        through_field = [k for k in all_fields if isinstance(k, ForeignKey) and issubclass(new_object.__class__, k.rel.to)][0]
                        for item in to_create[field] :
                            item.update({through_field.name:new_object, 'force':True})
                        new_objects = self.store(reverse_entity, to_create[field], starting_point=False)     
                elif aggregate[field]['type'] == 'reverse_o2o' :
                    reverse_entity = aggregate[field]['class']
                    to_create[field].update({aggregate[field]['field']:new_object})
                    new_objects = self.store(reverse_entity, [to_create[field]], starting_point=False)
                elif aggregate[field]['type'] == 'reverse_fk' :
                    reverse_entity = aggregate[field]['class']
                    for item in to_create[field] :
                        item.update({aggregate[field]['field']:new_object})
                    new_objects = self.store(reverse_entity, to_create[field], starting_point=False)
                elif aggregate[field]['type'] == 'reverse_m2m' :
                    reverse_entity = aggregate[field]['class']
                    new_objects = self.store(reverse_entity, to_create[field], starting_point=False)
                    for obj in new_objects :
                        getattr(obj, aggregate[field]['field']).add(new_object)
                elif aggregate[field]['type'] == 'generic_rel' :
                    reverse_entity = aggregate[field]['class']
                    for item in to_create[field] :
                        reverse_field = aggregate[field]['field']
                        if connect_to_base :
                            link = entity.__name__
                        else :
                            link = new_object.__class__.__name__
                        item.update({reverse_field:{'__target_class__':link, 'pk':new_object.pk}})
                    new_objects = self.store(reverse_entity, to_create[field], starting_point=False)   
         
    def _delegate_to_subclass(self, delegate, properties, subclass):
        """Delegate the creation to a subclass of entity."""
        field, item = delegate.items()[0]
        item.update(properties)
        child_entity = subclass[field]
        return self.store(child_entity, [item], starting_point=False)[0] 
    
    def _create_or_update(self, entity, pk, props):
        """Create or update an object."""
        #As pk is specified in the dictionary i.e. get_or_create cannot be used.
        if props.has_key('force') :
            force = props.pop('force')
        else :
            force = False
        pk_val = props[pk]
        obj_list = entity.objects.filter(pk=pk_val) 
        if obj_list.count() :
            if len(props) : 
                obj_list.update(**props)
            new_object = obj_list.get()
        else :
            new_object = entity.objects.create(**props)
        return new_object
    
    def _create_object(self, entity, pk, generic_fks, delegate, props, subcls):
        if len(delegate) :
            new_object = self._delegate_to_subclass(delegate, props, subcls)
        elif pk in props :
            new_object = self._create_or_update(entity, pk, props)
        else : 
            if props.has_key('force') :
                force = props.pop('force')
            else :
                force = False
            
            #User is a special case because an encrypted password has to be specified
            if issubclass(entity, User) :
                pwd_condition = props.has_key('password')
                password = props.pop('password') if pwd_condition else None
                created = True
            
            if not len(generic_fks) :
                if not force :
                    try :
                        new_object, created = entity.objects.get_or_create(**props)
                    except Exception, e :
                        #get returns more than one instance
                        #i.e. an indetermination arises 
                        #because fields that are useful to 
                        #identify an object are not stored in tmp 
                        logging.header("impossible to identify the good object with %s = %s (%s)" % (entity.__name__, props, e))
                        new_object = entity.objects.create(**props)
                else :
                    new_object = entity.objects.create(**props)
            else :
                new_dct = props.copy()
                for gfk in generic_fks :
                    gfk_obj = new_dct.pop(gfk)
                    ct_field = generic_fks[gfk]['ct_field']
                    fk_field = generic_fks[gfk]['fk_field']
                    new_dct[ct_field] = ContentType.objects.get_for_model(gfk_obj)
                    new_dct[fk_field] = gfk_obj.pk
                if not force :
                    objects = entity.objects.filter(**new_dct)
                    if objects.count() == 0 :
                        new_object = entity.objects.create(**new_dct)
                    elif objects.count() > 1 :
                        logging.header("impossible to identify the good object with %s = %s" % (entity.__name__, new_dct))
                        new_object = entity.objects.create(**new_dct)
                    elif objects.count() == 1 :
                        new_object = objects[0]
                else :
                    new_object = entity.objects.create(**new_dct)
            if issubclass(entity, User) and created :
                if password :
                    new_object.set_password(password)
                new_object.save()
        return new_object
     
    def store(self, entity, data, starting_point=True, connect_to_base=True):
        """Stores objects into the database."""
        created_objects = list()
        pk_id = [k for k in entity._meta.fields if k.primary_key][0].name
        foreign_keys, generic_foreign_keys, subclasses, many_related_fields = self._introspect_model(entity)
        _data = deepcopy(data) if starting_point else data
        for props in _data :
            class_name = props.__class__.__class__.__name__
            assert isinstance(props, dict) or (props.__class__.__name__ == 'Column') or (class_name == "ModelBase"), "objects must be a list of dictionaries or Column or ModelBase objects or ids."
            if class_name != "ModelBase" :
                tmp = self._cleanup(starting_point, props)
                filtered_many_related_fields = self._reorder(tmp, many_related_fields)
                to_create = self._to_create(filtered_many_related_fields, tmp)
                delegate = self._delegate(subclasses, tmp)
                transform = self.transform(tmp, foreign_keys, generic_foreign_keys, entity)
                logging.debug("Storing %s with properties %s" % (entity.__name__, props))
                new_object = self._create_object(entity, pk_id, generic_foreign_keys, delegate, transform, subclasses)
                self._attach_object(filtered_many_related_fields, to_create, new_object, connect_to_base, entity)   
            else :
                new_object = props           
            created_objects.append(new_object)
        return created_objects

class PopulateCommand(NoArgsCommand):
    """Base class that manages database population."""
    def __init__(self):
        super(PopulateCommand, self).__init__()
        self.populate = Populate()
    
    def handle_noargs(self, **options):
        logging.info('start %s' % self.help)
        for item in self.data :
            name = item['class']._meta.verbose_name_plural.lower()
            logging.info('start %s storage' % name)
            objects = self.populate.store(item['class'], item['objects'])
            
            if item.get('create_default_access_control') :
                for obj in objects : 
                    group = Group.objects.get(name="admin")
                    kwargs = {
                        'can_view':True,
                        'can_modify':True,
                        'can_delete':True,
                        'can_download':True,
                        'can_modify_permission':True
                    }
                    Permission.objects.create_group_permission(obj, group, **kwargs)
            logging.header("%s stored in database" % name)
        logging.info('%s finished' % self.help)
