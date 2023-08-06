#encoding:utf-8
from datetime import datetime
from django.db.models import Model
from helmholtz.editor.models import Entity

def get_schema(schema, child, record=None, key=None):
    if not schema :
        return None
    _cls = schema.content_type.model_class()
    new_schema = schema.get_child_entity(child, key)
    if new_schema :
        return new_schema.get_subclass_entity(record.__class__)
    elif _cls == child :
        return schema
    elif issubclass(_cls, child) or issubclass(child, _cls) :
        if not schema.parent :
            return schema
        else :
            _parent = schema.parent.cast()
            if isinstance(_parent, Entity) :
                return get_schema(_parent, child)
            else :
                return schema
#        return get_schema(schema.parent.cast(), child)
#        return schema.get_parent_entity(child)
    else :
        return None

def get_constraint(schema):
    return None if not schema or not schema.constraints.count() else schema.constraints.get().cast()

def get_displayed_value(record, notation):
    """Return human readable value."""
    try :
        obj_attr = getattr(record, notation)
    except :
        return None
    
    #replace the value by get_FOO_display function
    if isinstance(record, Model) :
        display_attr = getattr(record, 'get_%s_display' % notation, None)
        if display_attr :
            obj_attr = display_attr
    
    #replace the value by __unicode__ function
    if isinstance(obj_attr, Model) :
        obj_attr = obj_attr.__unicode__
    _tmp = obj_attr() if callable(obj_attr) else obj_attr
    return _tmp if not isinstance(_tmp, datetime) else datetime(_tmp.year, _tmp.month, _tmp.day, _tmp.hour, _tmp.minute, _tmp.second)

def get_value(record, notation):
    _chain = notation.split('.')
    _record = record
    if len(_chain) > 1 :
        for _attr in _chain[0:-1] :
            try :
                obj_attr = getattr(_record, _attr)
                if callable(obj_attr) :
                    obj_attr = obj_attr()
                _record = obj_attr
            except :
                return None
    return get_displayed_value(_record, _chain[-1]) if _record else None
