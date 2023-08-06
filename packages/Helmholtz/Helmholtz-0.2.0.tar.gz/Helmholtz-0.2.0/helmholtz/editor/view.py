#encoding:utf-8
from copy import copy, deepcopy
from django.db.models import ImageField, FileField, TextField, ForeignKey, OneToOneField
from django.db.models.related import RelatedObject
from django.db.models.loading import get_models
from django.utils.datastructures import SortedDict
from django.contrib.contenttypes.models import ContentType
from helmholtz.core.models import Cast, ObjectIndex, IntegerObjectIndex, CharObjectIndex
from helmholtz.core.schema import get_pk_type, \
                                  Field, \
                                  Link, \
                                  create_subclass_lookup, \
                                  self_referential_field, \
                                  get_subclasses_recursively, \
                                  regular_fields_objects, \
                                  foreign_keys_objects, \
                                  reverse_one_to_one_keys_objects, \
                                  many_to_many_fields_objects, \
                                  generic_relations_objects, \
                                  generic_foreign_keys_objects, \
                                  reverse_foreign_keys_objects, \
                                  reverse_many_to_many_fields_objects
from helmholtz.access_control.models import User, UnderAccessControlEntity, Permission
from helmholtz.annotation.models import Tag
from helmholtz.editor.shortcuts import get_schema, get_constraint, get_value
from helmholtz.editor.models import View as DBView, Section as DBSection, Entity as DBEntity, TableConstraint

#the following dictionary gives action priorities
action_weights = {
    'link':0,
    'add':1,
    'modify':2,
    'unlink':3,
    'delete':4
}

def set_expander(view_func):
    """
    Decorator used to update the expander
    right after nodes have been computed.
    """
    def modified_function(self):
        nodes = view_func(self)
        count = len(nodes)
        #determine expander and state 
        #from computed nodes count and
        #other internal parameters
        if not isinstance(self, Section) :
            condition = ((self.node_type == 'classnode') and self.displayed_in_navigator and bool(count)) or ((self.node_type != 'classnode') and bool(count)) 
        else :
            condition = bool(count)        
        if condition : 
            self._expander = True
        else :
            self._expander = False
            self._state = False
            self.view.states[self.index] = self._state
        #avoid displaying add action when max objects is reached
        if not isinstance(self, Section) :
            max_objects = getattr(self.constraint, 'max_objects', None)
            if not (max_objects is None) and (count >= max_objects) :
                if 'add' in self.displayed_actions :
                    self.displayed_actions.remove('add')
        return nodes
    modified_function.__doc__ = view_func.__doc__
    return modified_function

class CellNode(object):
    """Represent a cell when data are displayed in a table."""
    
    def __init__(self, view, parent, record, notation, position):
        self.view = view
        self.parent = parent
        self.record = record
        self.notation = notation
        self.position = position
        self.has_value = True
        if hasattr(record, notation) and isinstance(getattr(record, notation), (ImageField, FileField)) :
            field = record._meta.get_field_by_name(notation)[0]
            field_cls = field.__class__.__name__
        else :
            field_cls = ''
        self.is_file = (field_cls == 'FileField')
        self.is_image = (field_cls == 'ImageField')
        self.value = get_value(self.record, self.notation)
    
    @property
    def node_type(self):
        return "cellnode"
    
    @property
    def index(self):
        return self.parent.index + '.' + self.position

class BaseNode(object):
    """Node useful for the editor templates to completely reconstruct a View."""
    
    def __init__(self, view, parent, title, position, state=False, selection=False, is_root=False):
        self.view = view
        self.parent = parent
        self.title = title
        self.position = position
        self._selection = selection
        self.is_root = is_root  
        self._state = self.view.states.get(self.index, state)
        self._expander = True
    
    @property
    def node_type(self):
        """
        Return a verbose name given to BaseNode instance class.
        Each subclass must override this function and give a specific name.
        """
        return 'basenode'
    
    @property
    def index(self):
        """Return the unique index from the parent one and position number."""
        st = str(self.position)
        if self.parent :
            st = self.parent.index + '.' + st
        return st
    
    @property
    def node_model_index(self):
        """Return a unique index to cache node introspections."""
        title = get_title(self)
        parent = self.parent
        while parent :
            title = "%s_%s" % (get_title(parent), title)
            parent = parent.parent
        return title
    
    @property
    def type(self):
        """Return a verbose name for the BaseNode rooting type."""
        return 'root_node' if self.is_root else 'node'
    
    @property
    def state(self):
        """Return a verbose name for the BaseNode opening state."""
        return "closed" if not self._state else "opened"
    
    @property
    def selection(self):
        """Return a verbose name for the BaseNode selection state."""
        return "not_selected" if not self._selection else "selected"
    
    @property
    def expander(self):
        """Return a verbose name for the BaseNode expander state."""
        return "disabled" if not self._expander else "enabled"

class Node(BaseNode):
    """Node having an appearance customized by instances of editor models."""
    
    def __init__(self, view, parent, schema, title, position, state=False, selection=False, is_root=False):
        super(Node, self).__init__(view, parent, title, position, state, selection, is_root)
        self.schema = schema
    
    @property
    def node_type(self):
        return 'node'

class Section(Node):
    """Node useful to group ClassNode and sub Section objects."""
    
    def __init__(self, view, parent, schema, title, position, state=False, is_root=False):
        super(Section, self).__init__(view, parent, schema, title, position, state, False, is_root)
        self.nodes = list()
        #pre-computation of subsections and class nodes
        self._detail()
    
    @property
    def node_type(self):
        return 'basesection' if self.is_root else 'subsection'
    
    @set_expander
    def detail(self):
        if not self.nodes :
            self._detail()
        return self.nodes
    
    def _subsection_detail(self, schema):
        """Create sub Section objects under a Section object."""
        node = Section(self.view, self, schema, schema.title.title(), schema.position, is_root=False)
        self.view.sections[node.index] = node
        self.nodes.append(node)
        return node
    
    def _classnode_detail(self, schema):
        """Create ClassNode objects under a Section object."""
        model = schema.content_type.model_class()
        title = model._meta.verbose_name_plural
        node = ClassNode(self.view, self, schema, title.title(), schema.position)
        self.view.classes[node.index] = node
        self.nodes.append(node)
        return node
    
    def _detail(self):
        """
        Return sub Section and ClassNode objects 
        relative to a Section or a sub Section.
        """
        for child in self.schema.children.all() :
            schema = child.cast()
            if isinstance(schema, DBSection) :
                self._subsection_detail(schema)
            elif isinstance(schema, DBEntity) :
                self._classnode_detail(schema)
        
class FieldNode(BaseNode):
    """
    Node representing a field of an object that is not 
    a reference to single or set of database objects.
    """
    
    def __init__(self, view, parent, field, position):
        super(FieldNode, self).__init__(view, parent, field.verbose_name.lower(), position, False, False, False)
        self._expander = False
        self.has_value = True
        self.notation = field.name
        field_cls = field.__class__.__name__
        self.is_file = (field_cls == 'FileField')
        self.is_image = (field_cls == 'ImageField')
        self.is_text = isinstance(field, TextField)
        self.value = get_value(self.parent.record, self.notation)
        self.is_blank = isinstance(self.value, basestring) and not bool(self.value.strip())
        self.is_none = self.value is None
    
    @property
    def node_type(self):
        return 'fieldnode'

class PropertyNode(BaseNode):
    """Node representing a property computed from database object fields."""
    
    def __init__(self, view, parent, name, notation, position):
        super(PropertyNode, self).__init__(view, parent, name, position, False, False, False)
        self._expander = False
        self.has_value = True
        self.notation = notation
        self.value = get_value(self.parent.record, self.notation)
    
    @property
    def node_type(self):
        return 'propertynode'

class EntityNodeModel(object):
    """Node representing a relationship between database models."""
    
    def __init__(self, node_type, entity, schema, is_root):
        self.node_type = node_type
        self.entity = entity
        self.is_under_access_control = UnderAccessControlEntity.objects.is_registered(self.entity)
        self.content_type = ContentType.objects.get_for_model(entity)
        self.constraint = get_constraint(schema)
        self.actions = self._init_base_actions()

    def _init_base_actions(self):
        """Return user defined actions for a node.""" 
        all_actions = set(['add', 'modify', 'delete', 'link', 'unlink'])
        actions = set()
        if self.constraint :
            if self.constraint.actions.count() :
                #update with user defined actions
                defined_actions = set([k.get_name_display() for k in self.constraint.actions.all()])
                if not 'none' in defined_actions :
                    actions.update(defined_actions)
            else :
                #update with all possible actions
                actions.update(all_actions)
        return list(actions)

class ObjectNodeModel(EntityNodeModel):
    
    def __init__(self, entity, schema, is_root):
        super(ObjectNodeModel, self).__init__('objectnode', entity, schema, is_root)
        self.shunt = getattr(self.constraint, 'shunt', True)

class EntityReferenceNodeModel(EntityNodeModel):

    def __init__(self, node_type, entity, schema, is_root, view):
        super(EntityReferenceNodeModel, self).__init__(node_type, entity, schema, is_root)
        self.in_expansion = list()
        self.cto_fields = SortedDict()
        self.excluded_subclasses = list()
        self.subclasses = list()
        self._init_introspection(view)
        self.subclasses = self._init_subclasses(view)
        #enumerate id of subclasses only
        if (len(self.subclasses) == 1) :
            self.subclass_id = ''
            new_entity = self.subclasses[0]
            new_schema = get_schema(schema, new_entity)
            super(EntityReferenceNodeModel, self).__init__(node_type, new_entity, new_schema, is_root) 
        else :
            self.subclass_id = ','.join([str(ContentType.objects.get_for_model(k).pk) for k in self.subclasses])
    
    def _init_introspection(self, view):
        if self.constraint :
            self.in_expansion.extend([(k.identifier, k.verbose_name if k.verbose_name else None) for k in self.constraint.in_expansion.order_by('inexpansion__pk')])
        
        #copy fields from view introspection
        #and filter them by user defined choices
        keys = ['fkeys', 'ro2o', 'm2m', 'rfks', 'rm2m', 'grs', 'gfkeys', 'fields']
        in_expansion = list()
        for key in keys :
            fields = deepcopy(view.introspections[self.entity][key])
            if self.in_expansion :
                to_exclude = [k for k in fields if not (k, None) in self.in_expansion]
                for field in to_exclude :
                    fields.pop(field, None)  
            else :
                in_expansion.extend([(k, None) for k in fields])
            setattr(self, key, fields)
        
        if not self.in_expansion :
            self.in_expansion.extend(in_expansion)
        
        #adding fields relative to a ObjectIndex
        #keep only fields specifying permissions and tags
        #that is object_permissions and tag_set accessors
        #and maybe access requests later ... if useful
        cto_fields = ['object_permissions', 'tag_set']
        cls = IntegerObjectIndex if (get_pk_type(self.entity) == int) else CharObjectIndex
        if not self.in_expansion :
            if self.is_under_access_control :
                self.in_expansion.extend([('object_permissions', None)])
                self.cto_fields['object_permissions'] = deepcopy(view.introspections[cls]['rfks']['object_permissions'])
            self.in_expansion.extend([('tag_set', None)])
            self.cto_fields['tag_set'] = deepcopy(view.introspections[cls]['rm2m']['tag_set'])  
        else :
            if ('object_permissions', None) in self.in_expansion :
                pos = self.in_expansion.index(('object_permissions', None))
                if not self.is_under_access_control :
                    self.in_expansion.pop(pos)
                else :
                    self.cto_fields['object_permissions'] = deepcopy(view.introspections[cls]['rfks']['object_permissions'])
            if ('tag_set', None) in self.in_expansion :
                self.cto_fields['tag_set'] = deepcopy(view.introspections[cls]['rm2m']['tag_set'])
    
    def _init_subclasses(self, view):
        if self.constraint :
            self.excluded_subclasses.extend([k.model_class() for k in self.constraint.excluded_subclasses.all()])
        subclasses = [k for k in view.introspections[self.entity]['subclasses'] if not k in self.excluded_subclasses]
        strict = not getattr(self.constraint, 'display_base_class', False)
        is_base = not issubclass(self.entity, Cast) or (self.entity is self.entity.get_base_class())
        if subclasses and strict and is_base :
            index = subclasses.index(self.entity)
            subclasses.pop(index)
        return subclasses

class ObjectLinkModel(EntityReferenceNodeModel):
    
    def __init__(self, entity, schema, is_root, view, from_link_list=False):
        super(ObjectLinkModel, self).__init__('objectlink', entity, schema, is_root, view)
        self.shunt = getattr(self.constraint, 'shunt', True)
        self.from_link_list = from_link_list
        if not self.from_link_list :
            self.has_value = True
        else :
            self.has_value = False

class BaseClassNodeModel(EntityReferenceNodeModel):
    
    def __init__(self, node_type, entity, schema, is_root, parent_node_type, view):
        super(BaseClassNodeModel, self).__init__(node_type, entity, schema, is_root, view)
        self.in_header = list()
        self.groupers = SortedDict()
        #subclasses
        self.display_subclasses = getattr(self.constraint, 'display_subclasses', False)
        self.is_root_class = (not parent_node_type in ['classnode', 'listoflinks'])
        self.is_subclassed = self.display_subclasses and self.is_root_class and bool(self.subclasses)
        #table and expander
        self.as_table = isinstance(self.constraint, TableConstraint) if self.constraint else False
        self.width = None
        if self.as_table :
            self.pagination = getattr(self.constraint, 'pagination', 25)
            self.width = self.constraint.width
            self.in_header = self._init_header()
            self.rowspan = 2 if self.groupers else 1
            self.header_columns = self.count_header_columns()
            self.footer_columns = self.header_columns + 1
        else :
            self.pagination = None
        self.displayed_in_navigator = False
    
    def _append_item(self, item, destination):
        if item.verbose_name :
            destination.append((item.identifier, item.verbose_name))
        else :
            field = self.entity._meta.get_field_by_name(item.identifier)[0]
            if isinstance(field, RelatedObject) :
                if isinstance(field.field, ForeignKey) or isinstance(field.field, OneToOneField) :
                    destination.append((field.get_accessor_name(), field.model._meta.verbose_name)) 
                else :
                    destination.append((field.get_accessor_name(), field.model._meta.verbose_name_plural))   
            else :
                destination.append((field.name, field.verbose_name))
    
    def _init_header(self):
        """
        Return a list of (name, verbose_name) tuples 
        representing the content of an header.
        """
        in_header = list()
        defined_header = self.constraint.in_header.order_by('inheader__pk')
        if defined_header :
            for item in defined_header :
                if not item.is_grouper and item.identifier != 'recording_point' : #HACK: prevent template error
                #if not item.is_grouper :
                    self._append_item(item, in_header)
                else :
                    items = list()
                    for it in item.subfields.all() :
                        self._append_item(it, items)
                    self.groupers[item.identifier] = items
                    in_header.append((item.identifier, items))
        else :
            in_header.append(('pk', None))
        return in_header
    
    def count_header_columns(self):
        """Return the number of columns constituting a table header."""
        count = -len(self.groupers)
        for items in self.groupers.values() :
            count += len(items)
        return len(self.in_header) + count

class ClassNodeModel(BaseClassNodeModel):
    
    def __init__(self, entity, schema, is_root, parent_node_type, view):
        super(ClassNodeModel, self).__init__('classnode', entity, schema, is_root, parent_node_type, view)
        #link and unlink actions cannot be available for a ClassNode object
        if 'link' in self.actions :
            self.actions.pop(self.actions.index('link'))
        if 'unlink' in self.actions :
            self.actions.pop(self.actions.index('unlink'))
        self.displayed_in_navigator = getattr(self.constraint, 'displayed_in_navigator', False)

class BaseListOfLinkNodeModel(BaseClassNodeModel):
    
    def __init__(self, node_type, entity, schema, is_root, parent_node_type, view, key, link):
        super(BaseListOfLinkNodeModel, self).__init__(node_type, entity, schema, is_root, parent_node_type, view)
        #the couple record, key is prefered 
        #because a RelatedManager cannot be pickled
        self.key = key    
        self.link = link

class ListOfLinkNodeModel(BaseListOfLinkNodeModel):
     
    def __init__(self, entity, schema, is_root, parent_node_type, view, key, link):
        super(ListOfLinkNodeModel, self).__init__('listoflinks', entity, schema, is_root, parent_node_type, view, key, link)

class SubclassNodeModel(BaseListOfLinkNodeModel):
    
    def __init__(self, entity, schema, is_root, parent_node_type, view, key, link):
        super(SubclassNodeModel, self).__init__('subclassnode', entity, schema, is_root, parent_node_type, view, key, link)

def get_title(node):
    if isinstance(node, (Section, ClassNode)) :
        return node.title
    elif isinstance(node, (ObjectNode, ObjectLink)) :
        return node.entity._meta.verbose_name.lower()
    elif isinstance(node, (BaseListOfLink)):
        return node.link.verbose_name.lower()

class EntityNode(Node):
    """
    Wrap everything concerning a database model
    in a structure able to generate single or set 
    of instances relative to this model.
    """ 
    
    def __init__(self, model, view, parent, entity, schema, title, position, state=False, selection=False, is_root=False):
        super(EntityNode, self).__init__(view, parent, schema, title, position, state, selection, is_root)
        self.model = model
        self.displayed_actions = set()
        self.inactive_actions = set()
    
    @property
    def node_type(self):
        return self.model.node_type

    @property
    def entity(self):
        return self.model.entity
    
    @property
    def content_type(self):
        return self.model.content_type
    
    @property
    def constraint(self):
        return self.model.constraint
    
    @property
    def actions(self):
        return self.model.actions
    
    def ordered_displayed_actions(self):
        """Return a list containing displayed_actions ordered by weights."""
        actions = list(self.displayed_actions)
        actions.sort(key=lambda x:action_weights[x], reverse=True)
        return actions
    
    @property
    def _class_id(self):
        return getattr(self.content_type, 'pk', None)
    
    @property
    def _constraint_id(self):
        return getattr(self.constraint, 'pk', None)
    
    def request_parameters(self):
        pattern = unicode()
        parameters = self.get_parameters()
        for k in parameters :
            value = getattr(self, "_" + k)
            if not value is None and value :
                pattern += "&%s=%s" % (k, value)
        return pattern[1:]
    
    @classmethod
    def get_parameters(self):
        raise NotImplementedError("must be implemented in subclasses")
    
class BaseObjectNode(EntityNode):
    """Subclass of EntityNode wrapping a database object."""
    
    def __init__(self, model, view, parent, entity, schema, title, record, position, state=False):
        self.record = record
        super(BaseObjectNode, self).__init__(model, view, parent, entity, schema, title, position, state)
        self._expander = bool(self.record) and not self.shunt
        #access control
        if self.record :
            self.is_accessible = self.view.user.can_view(self.record)
            self.is_editable = self.view.user.can_edit(self.record)
            self.is_deletable = self.view.user.can_delete(self.record)
            self.is_downloadable = self.view.user.can_download(self.record)
            self.is_owned_by_user = self.view.user.is_owner(self.record)
        else :
            self.is_accessible = False
            self.is_editable = False
            self.is_deletable = False
            self.is_downloadable = False
            self.is_owned_by_user = False

    @property
    def shunt(self):
        return self.model.shunt

    @property
    def index(self):
        if not (isinstance(self.parent, BaseClassNode) and self.parent.as_table) :
            return super(BaseObjectNode, self).index
        else :
            return self.parent.index + '.' + str(self.record.pk) 
    
    def _fake_link(self, parent, link, key, nodes):
        """Collapse a list containing a single element to a single ObjectLink."""
        records = self.view.user.get_accessible(getattr(self.record, key).all())
        record = records.get() if records else None
        _record = record.cast() if isinstance(record, Cast) else record
        schema = get_schema(parent.schema, link.klass, _record)
        position = parent._position(key)
        node = ObjectLink(self.view, self, schema, link, _record, position, is_fake_object_link=True)
        nodes.append(node)
    
    def _listoflink(self, parent, schema, link, key, nodes):
        """
        Create an ListOfLink node representing a list of objects 
        generated by reverse foreign keys or reverse many to many fields.
        """
        position = parent._position(key)
        node = ListOfLink(self.view, self, schema, link, self.record, key, position)
        nodes.append(node)
    
    def _listoflinks(self, parent, attribute, nodes):
        """
        Create nodes corresponding to object many to many fields, 
        reverse foreign keys or reverse many to many fields.
        """
        for key, link in attribute.items() :
            schema = get_schema(parent.schema, link.klass, key=key)
            constraint = get_constraint(schema)
            is_fake = not (constraint is None) and not constraint.display_subclasses and not isinstance(constraint, TableConstraint) and (constraint.max_objects < 2) and not (constraint.max_objects is None)
            self._fake_link(parent, link, key, nodes) if is_fake else self._listoflink(parent, schema, link, key, nodes)
            
    def _cto_fields(self, parent, nodes):
        """
        Create nodes corresponding to content type object object_permissions and tag_set fields.
        """
        for key, link in parent.cto_fields.items() :
            if (issubclass(link.klass, Permission) and self.is_owned_by_user) or (issubclass(link.klass, Tag) and self.is_editable) :
                schema = get_schema(parent.schema, link.klass)
                position = parent._position(key)
                record = ObjectIndex.objects.get_registered_object(self.record) if self.record else None
                node = ListOfLink(self.view, self, schema, link, record, key, position)
                nodes.append(node)
    
    def _fields(self, entity, parent, attribute, nodes) :
        """Create FieldNode objects corresponding to object fields."""
        for field_name in attribute :
            field = entity._meta.get_field_by_name(field_name)[0]
            position = parent._position(field_name)
            node = FieldNode(self.view, self, field, position)
            nodes.append(node)
    
    def _gfkeys(self, parent, attribute, nodes) :
        """Create FieldNode objects corresponding to object generic foreign keys."""
        for field_name in attribute :
            field = self.parent.entity._meta.get_field_by_name(field_name)[0]
            position = parent._position(field_name)
            node = FieldNode(self.view, self, field, position)
            nodes.append(node)
    
    def _properties(self, parent, attribute, nodes) :
        """Create PropertyNode objects corresponding to object properties."""
        for name, verbose_name in attribute :
            position = parent._position(name, verbose_name)
            node = PropertyNode(self.view, self, verbose_name, name, position)
            nodes.append(node)
    
    def _links(self, parent, attribute, nodes) :
        """Create ObjectLink objects corresponding to object foreign keys or reverse one to one fields."""
        for key, link in attribute.items() :
            try :
                record = getattr(self.record, key, None)
            except :
                record = None
            _record = record.cast() if isinstance(record, Cast) else record
            schema = get_schema(parent.schema, link.klass, _record, key)
            position = parent._position(key)
            node = ObjectLink(self.view, self, schema, link, _record, position)
            nodes.append(node)  
    
    def detail(self):
        """Create all nodes corresponding to object attributes."""
        nodes = list()
        if self.record :
            
            if self.node_type == 'objectlink' :
                parent = self
            elif self.node_type == 'objectnode' :
                parent = self.parent
            else :
                raise Exception(self.node_type)

            #fields
            self._fields(self.entity, parent, parent.fields, nodes)
            
            #properties
            properties = [k for k in parent.in_expansion if k[1]]
            self._properties(parent, properties, nodes)
            
            #foreign keys, one to one fields, reverse one to one fields and generic foreign keys
            self._links(parent, parent.fkeys, nodes)
            self._links(parent, parent.ro2o, nodes)
            #self._gfkeys(self.parent.fields, nodes, position)
            
            #many to many fields, generic relations, reverse foreign keys and many to many fields
            self._listoflinks(parent, parent.m2m, nodes)
            self._listoflinks(parent, parent.grs, nodes)
            self._listoflinks(parent, parent.rfks, nodes)
            self._listoflinks(parent, parent.rm2m, nodes)
            
            #content type object fields
            self._cto_fields(parent, nodes)
            
            #candidate generic relations
            #self._ctobjects(parent, parent.candidate_grs, nodes)
            
            #sort by position
            nodes.sort(key=lambda x : x.position)
               
        return nodes
    
    def cell_nodes(self):
        """Create all nodes corresponding to table cells."""
        nodes = list()
        for item in self.parent.in_header :
            if not isinstance(item[1], list) :
                position = self.parent.in_header.index(item)
                node = CellNode(self.view, self, self.record, item[0], position)
                nodes.append(node)
            else :
                #when fields are grouped into another field
                for it in item[1] :
                    position = item[1].index(it)
                    node = CellNode(self.view, self, self.record, it[0], position)
                    nodes.append(node)
        return nodes
    
    @property
    def _object_id(self):
        return getattr(self.record, 'pk', None)
    
    @property
    def _parent_node_type(self):
        return getattr(self.parent, 'node_type', None)

class EntityReferenceNodeProxyProperties(object):
    """
    A convenient class used as a proxy to access
    EntityReferenceNodeModel properties and inherited
    in BaseClassNode and ObjectLink classes.
    """
      
    @property
    def in_expansion(self):
        return self.model.in_expansion

    @property
    def excluded_subclasses(self):
        return self.model.excluded_subclasses
    
    @property
    def subclasses(self):
        return self.model.subclasses
    
    @property
    def subclass_id(self):
        return self.model.subclass_id
    
    @property
    def _subclass_id(self):
        id = self.model.subclass_id
        return id if id else None
    
    @property
    def _field(self):
        return self.link.name
    
    @property
    def _reverse(self):
        return str(int(self.link.reverse))
    
    @property
    def fields(self):
        return self.model.fields
    
    @property
    def fkeys(self):
        return self.model.fkeys
    
    @property
    def ro2o(self):
        return self.model.ro2o
    
    @property
    def m2m(self):
        return self.model.m2m
    
    @property
    def rfks(self):
        return self.model.rfks
    
    @property
    def rm2m(self):
        return self.model.rm2m
    
    @property
    def grs(self):
        return self.model.grs
    
    @property
    def gfkeys(self):
        return self.model.gfkeys
    
    @property
    def cto_fields(self):
        return self.model.cto_fields
    
    @property
    def candidate_grs(self):
        return self.model.candidate_grs

class BaseClassNode(EntityNode, EntityReferenceNodeProxyProperties):
    """Subclass of EntityNode wrapping a database model."""    
    
    def __init__(self, model, view, parent, entity, schema, title, position, state=False, selection=False, is_root=False):
        super(BaseClassNode, self).__init__(model, view, parent, entity, schema, title, position, state, selection, is_root)
        self.nodes = list()
        self.n_pages = None
        self._records = None
        if self.as_table :
            self.page = 1 if not self.view.pages.has_key(self.index) else self.view.pages[self.index]
            self._init_order_by()
            self.ordering = 'ascending' if not self.view.ordering.has_key(self.index) else self.view.ordering[self.index]
        else :
            self.page = None
        self.children_actions = set()
    
    @property
    def in_header(self):
        """
        Return fields displayed in the header 
        of a table containing model instances data.
        """
        return self.model.in_header
    
    @property
    def groupers(self):
        """Return fields grouping other fields in a table header."""
        return self.model.groupers
    
    @property
    def display_subclasses(self):
        return self.model.display_subclasses
    
    @property
    def is_root_class(self):
        return self.model.is_root_class
    
    @property
    def is_subclassed(self):
        return self.model.is_subclassed
    
    @property
    def as_table(self):
        return self.model.as_table
    
    @property
    def width(self):
        return self.model.width
    
    @property
    def pagination(self):
        return self.model.pagination
    
    @property
    def rowspan(self):
        return self.model.rowspan
    
    @property
    def header_columns(self):
        return self.model.header_columns
    
    @property
    def footer_columns(self):
        return self.model.footer_columns
    
    @property
    def displayed_in_navigator(self):
        return self.model.displayed_in_navigator
    
    def _init_order_by(self):
        if not self.view.order_by.has_key(self.index) :
            if not isinstance(self.in_header[0][1], tuple) :
                self.order_by = self.in_header[0][0]
            else :
                self.order_by = self.in_header[0][1][0]
        else :
            self.order_by = self.view.order_by[self.index]
    
    def _position(self, name, notation=None):
        return self.in_expansion.index((name, notation))
    
    def expansion_colspan(self):
        return self.header_columns + len(self.children_actions) + 1
    
    def sort_table(self, nodes):
        nodes.sort(key=lambda x:get_value(x.record, self.order_by))
        if self.ordering == 'descending' :
            nodes.reverse()
    
    def limit_table(self, nodes):
        """
        Return only nodes corresponding to the selected
        table page and the defined pagination.
        """
        upper_bound = self.page * self.pagination
        lower_bound = upper_bound - self.pagination
        if self.page != self.n_pages :
            new_nodes = nodes[lower_bound:upper_bound]
        else :
            new_nodes = nodes[lower_bound:] 
        return new_nodes
    
    def get_records(self):
        """Return the ordered list of accessible objects."""
        #avoid displaying children of a hierarchy on the first level of display
        hierarchy = getattr(self.constraint, 'hierarchy', False)
        if not hierarchy or (self.node_type in ['listoflinks', 'subclassnode']) :
            records = self.manager.all() 
        else :
            field = self_referential_field(self.manager.model)
            dct = {field.name + '__isnull':True}
            records = self.manager.filter(**dct)
        
        #for base class node just keep object that are not corresponding to subclasses
        if self.parent.node_type in ['classnode', 'listoflinks'] and (self.parent.entity == self.entity) and self.parent.display_subclasses and self.parent.is_root_class :
            lookups = [create_subclass_lookup(k) for k in self.subclasses if (k != self.entity)]
            lookup_dct = dict()
            for lookup in lookups :
                lookup_dct[lookup + '__isnull'] = True
            records = records.filter(**lookup_dct)
        
        #keep only objects accessible by the user
        records = self.view.user.get_accessible(records)

        return records
    
    def page_range(self):
        """Return the range of pages splitting table data on several panels."""
        if not self.as_table or self.n_pages == 1 :
            return None
        else :
            return range(1, self.n_pages + 1)
    
    def init_pages(self, object_count):
        """
        Refresh the number of pages splitting table
        data on several panels. After refreshing, 
        set the current page equal to this number
        if it is greater than this one.
        """
        n, r = divmod(object_count, self.pagination)
        self.n_pages = n + int(bool(r))
        if self.page > self.n_pages :
            self.page = self.n_pages 
    
    @set_expander
    def detail(self):
        """Return nodes corresponding to the objects to display in the editor."""
        nodes = list()
        position = 0
        records = self.get_records()
        
        #as the editor manage sorting by a key that is not an object field
        #it is necessary to store all objects and then select whose will be displayed
        for record in records :
            node = self.get_node_object(record, position)
            nodes.append(node)
            position += 1   
        
        #if they are displayed in a table :
        # - update the current displayed page
        # - set up the number of pages
        # - sort and paginate objects 
        if self.as_table :
            self.init_pages(len(nodes))
            self.sort_table(nodes)
            nodes = self.limit_table(nodes)
        
        return nodes

class BaseListOfLink(BaseClassNode):
    """
    Subclass of BaseClassNode wrapping a database model 
    and used to generate instances of this class from 
    forward or backward relationships materialized by
    many to many fields, reverse foreign keys, reverse
    one to one fields or reverse many to many fields.
    """ 
    
    def __init__(self, model, view, parent, schema, link, record, key, entity, title, position, state=False):
        super(BaseListOfLink, self).__init__(model, view, parent, entity, schema, title, position, state)
        self.record = record

    @property
    def key(self):
        return self.model.key
    
    @property
    def link(self):
        return self.model.link

    @property
    def has_value(self):
        return not self._expander
    
    def get_node_object(self, record, position):
        _record = record.cast() if isinstance(record, Cast) else record
        schema = self.schema if (_record.__class__ == self.entity) else get_schema(self.schema, _record.__class__)
        return ObjectLink(self.view, self, schema, self.link, _record, position, from_link_list=True)

    @property
    def manager(self):
        return getattr(self.record, self.key)

class ObjectNode(BaseObjectNode):
    """
    Subclass of BaseObjectNode wrapping a database
    object generated by the database model main Manager.
    """
    
    def __init__(self, view, parent, schema, record, position, state=False):
        _record = record.cast() if isinstance(record, Cast) else record
        #find the model in the view node_models cache
        index = "%s_%s" % (parent.node_model_index, _record.__class__._meta.verbose_name.lower())
        if not index in view.node_models :
            model = ObjectNodeModel(_record.__class__, schema, False)
            view.node_models[index] = model
        else :
            model = view.node_models[index]
        super(ObjectNode, self).__init__(model, view, parent, _record.__class__, schema, _record, _record, position, state) 
        self.init_actions_to_display()
    
    def init_actions_to_display(self):
        self.displayed_actions = self.parent.children_actions
        if ('delete' in self.parent.actions) :
            if not self.is_deletable :
                self.inactive_actions.add('delete')   
        if ('modify' in self.parent.actions) :
            if not self.is_editable :
                self.inactive_actions.add('modify')
    
    @property
    def _constraint_id(self):
        return getattr(self.parent.model.constraint, 'pk', None)
    
    @property
    def _parent_node_type(self):
        return getattr(self.parent, 'node_type', None)
    
    @classmethod
    def get_parameters(cls):
        return [
            'class_id',
            'object_id',
            'parent_node_type',
            'constraint_id'
        ]

class ObjectLink(BaseObjectNode, EntityReferenceNodeProxyProperties):
    """
    Subclass of BaseObjectNode wrapping a database object generated
    by forward or backward relationships materialized by foreign keys,
    one to one fields or reverse one to one fields.
    """
    
    def __init__(self, view, parent, schema, link, record, position, state=False, from_link_list=False, is_fake_object_link=False):
        self.is_fake_object_link = is_fake_object_link
        _record = record.cast() if isinstance(record, Cast) else record
        cls = _record.__class__ if record else link.klass
        if not from_link_list :
            self.superclass_title = link.verbose_name
            title = link.verbose_name
            if record and cls != link.klass :
                title += " / " + record.__class__._meta.verbose_name 
            value = record
        else :
            title = record
            self.superclass_title = None
            value = None
        #find the model in the view node_models cache
        st = "%s_%s" % (parent.node_model_index, link.klass._meta.verbose_name.lower())
        if record :
            st += "_%s" % cls._meta.verbose_name.lower()
        index = st + "_objectlink"
        if not index in view.node_models :
            model = ObjectLinkModel(cls, schema, False, view, from_link_list)
            view.node_models[index] = model
        else :
            model = view.node_models[index]
        super(ObjectLink, self).__init__(model, view, parent, cls, schema, title, _record, position, state)    
        self.value = value
        self.link = link
        self.init_actions_to_display()
        #find parent for request parameters
        _parent = self.parent
        __parent = _parent.parent
        dct = {
            "subclassnode":__parent.parent,
            "listoflinks":__parent,
        }
        self._parent = dct.get(_parent.node_type, _parent)
    
    @property
    def from_link_list(self):
        return self.model.from_link_list
    
    @property
    def has_value(self):
        return self.model.has_value
    
    def _position(self, name, notation=None):
        return self.in_expansion.index((name, notation))
    
    def init_actions_to_display(self):
        if self.parent.node_type in ["listoflinks", "subclassnode"] :
            if self.parent.node_type == "listoflinks" :
                parent = self.parent.parent
            else :
                parent = self.parent.parent.parent
            self.displayed_actions = self.parent.children_actions
            
            #remove unlink action for fake object links
            if 'unlink'in self.displayed_actions and self.is_fake_object_link :
                self.displayed_actions.remove('unlink')
            
            if 'delete' in self.displayed_actions :
                if not self.is_deletable :
                    self.inactive_actions.add('delete')
                elif not (self.is_deletable and parent.is_editable) :
                    self.inactive_actions.add('delete')
            if 'modify' in self.displayed_actions :
                if not self.is_editable :
                    self.inactive_actions.add('modify')
                if not self.link.required :
                    if 'unlink' in self.displayed_actions :
                        if self.link.reverse :
                            if not self.is_editable :
                                self.inactive_actions.add('unlink')
                        elif 'modify' in parent.actions :
                            if not parent.is_editable :
                                self.inactive_actions.add('unlink')
        else :
            #add
            if ('add' in self.actions) and not (self.parent.node_type in ["listoflinks", "subclassnode"]) and not self.value :
                if self.link.reverse :
                    self.displayed_actions.add('add')
                elif "modify" in self.parent.actions :
                    self.displayed_actions.add('add')
                    if not self.parent.is_editable :
                        self.inactive_actions.add('add')
            #delete
            if ('delete' in self.actions) :
                if not (self.parent.node_type == "listoflinks") and self.value and not self.link.required :
                    if self.link.reverse :
                        self.displayed_actions.add('delete')
                        if not self.is_deletable :
                            self.inactive_actions.add('delete')
                    elif 'modify' in self.parent.actions :
                        self.displayed_actions.add('delete')
                        if not (self.is_deletable and self.parent.is_editable) :
                            self.inactive_actions.add('delete')
                elif self.parent.node_type == "subclassnode" and not self.link.required :
                    if self.link.reverse :
                        self.displayed_actions.add('delete')
                        if not self.is_deletable :
                            self.inactive_actions.add('delete')
                    elif 'modify' in self.parent.parent.parent.actions :
                        self.displayed_actions.add('delete')
                        if not (self.is_deletable and self.parent.parent.parent.is_editable) :
                            self.inactive_actions.add('delete')
            #modify
            if 'modify' in self.actions :
                if 'link' in self.actions and not self.parent.node_type in ["listoflinks", "subclassnode"] and not self.link.required and not self.value :
                    if self.link.reverse :
                        self.displayed_actions.add('link')
                        #if not self.is_editable :
                        #self.inactive_actions.add('link')
                    elif 'modify' in self.parent.actions :
                        self.displayed_actions.add('link')
                        if not self.parent.is_editable :
                            self.inactive_actions.add('link')
                elif 'unlink' in self.actions and not self.parent.node_type in ["listoflinks", "subclassnode"] and not self.link.required and self.value :
                    if self.link.reverse :
                        self.displayed_actions.add('unlink')
                        if not self.is_editable :
                            self.inactive_actions.add('unlink')
                    elif 'modify' in self.parent.actions :
                        self.displayed_actions.add('unlink')
                        if not self.parent.is_editable :
                            self.inactive_actions.add('unlink')
                elif self.parent.node_type == "subclassnode" :
                    self.displayed_actions.add('modify')
                    if not self.is_editable :
                        self.inactive_actions.add('modify')
                    if 'unlink' in  self.actions and not self.link.required :
                        if self.link.reverse :
                            self.displayed_actions.add('unlink')
                            if not self.is_editable :
                                self.inactive_actions.add('unlink')
                        elif 'modify' in self.parent.parent.parent.actions :
                            self.displayed_actions.add('unlink')
                            if not self.parent.parent.parent.is_editable :
                                self.inactive_actions.add('unlink')
                if not self.parent.node_type in ["listoflinks", "subclassnode"] and self.value :
                    self.displayed_actions.add('modify')
                    if not self.is_editable :
                        self.inactive_actions.add('modify')
                    
                    #for fake object links
                    if self.is_fake_object_link and self.parent.is_editable :
                        self.displayed_actions.add('delete')
                        if not self.is_deletable :
                            self.inactive_actions.add('delete')
    
    @property
    def _parent_class_id(self):
        return self._parent.content_type.pk
    
    @property
    def _parent_object_id(self):
        return self._parent.record.pk
    
    @classmethod
    def get_parameters(cls):
        return [
            'class_id',
            'object_id',
            'parent_node_type',
            'parent_class_id',
            'parent_object_id',
            'field',
            'reverse',
            'constraint_id',
            'subclass_id'
        ]

class ClassNode(BaseClassNode):
    """
    Subclass of BaseClassNode wrapping a database model and used
    to generate instances of this model from its main Manager.
    """
    
    def __init__(self, view, parent, schema, title, position, state=False, selection=False, is_root=False):
        entity = schema.content_type.model_class()
        index = "%s_%s" % (parent.node_model_index, title)
        if not index in view.node_models :
            model = ClassNodeModel(entity, schema, is_root, parent.node_type, view)
            view.node_models[index] = model
        else :
            model = view.node_models[index]
        #if there's only one subclass the created ClassNode instance
        #will be a reference to this unique subclass
        if (entity != model.entity) :
            _entity = model.entity
            _title = _entity._meta.verbose_name_plural.title()
            _schema = get_schema(schema, _entity)
        else :
            _entity = entity
            _title = title
            _schema = schema
        super(ClassNode, self).__init__(model, view, parent, _entity, _schema, _title, position, state, selection, is_root)
        #cache subclasses sections
        if self.is_subclassed :
            self.init_subclass_nodes()
        self.init_actions_to_display()
    
    @property
    def displayed_in_navigator(self):
        return self.model.displayed_in_navigator
    
    def init_state(self, object_count):
        self._state = self._expander and (self.subclasses) 
    
    def init_actions_to_display(self):
        if not ('add' in self.displayed_actions) and ('add' in self.actions) and not self.display_subclasses :
            self.displayed_actions.add('add')
        if not ('delete' in self.children_actions) and ('delete' in self.actions) :
            self.children_actions.add('delete')  
        if not ('modify' in self.children_actions) and ('modify' in self.actions)  :
            self.children_actions.add('modify')
    
    def init_subclass_nodes(self):
        position = 0
        for subclass in self.subclasses :
            title = subclass._meta.verbose_name_plural
            schema = get_schema(self.schema, subclass)
            node = ClassNode(self.view, self, schema, title.title(), position)
            self.view.classes[node.index] = node
            self.nodes.append(node)
            position += 1
    
    @property
    def manager(self):
        return self.entity.objects
 
    def get_node_object(self, record, position):
        _record = record.cast() if isinstance(record, Cast) else record
        schema = self.schema if (record.__class__ == self.entity) else get_schema(self.schema, _record.__class__)
        return ObjectNode(self.view, self, schema, record, position)
 
    @set_expander
    def detail(self):
        if self.nodes :
            return self.nodes
        else :
            return super(ClassNode, self).detail()
    
    @classmethod
    def get_parameters(cls):
        return [
            'class_id',
            'constraint_id',
            'subclass_id'
        ]

class ListOfLink(BaseListOfLink):
    """
    Subclass of BaseListOfLink.
    """
    
    def __init__(self, view, parent, schema, link, record, key, position, state=False): 
        #find the model in the view node_models cache
        index = "%s_%s_listoflinks" % (parent.node_model_index, link.verbose_name)
        if not index in view.node_models :
            model = ListOfLinkNodeModel(link.klass, schema, False, parent.node_type, view, key, link)
            view.node_models[index] = model
        else :
            model = view.node_models[index]
        super(ListOfLink, self).__init__(model, view, parent, schema, link, record, key, link.klass, link.verbose_name, position, state)
        self.init_actions_to_display()
        self.value = None
    
    def init_actions_to_display(self) :
        #actions to display on screen
        #add
        if ('add' in self.actions) and not self.display_subclasses :
            if self.link.reverse :
                self.displayed_actions.add('add')
            elif 'modify' in self.parent.actions :
                self.displayed_actions.add('add')
                if not self.parent.is_editable :
                    self.inactive_actions.add('add')
        #delete
        if 'delete' in self.actions :
            if self.link.reverse or 'modify' in self.parent.actions :
                self.children_actions.add('delete')
        #modify
        if 'modify' in self.actions :
            if 'unlink' in self.actions and (self.link.reverse or 'modify' in self.parent.actions) :
                self.children_actions.add('unlink')
            self.children_actions.add('modify')
            if not self.display_subclasses :
                if 'link' in self.actions :
                    if self.link.reverse :
                        self.displayed_actions.add('link')
                    elif 'modify' in self.parent.actions :
                        self.displayed_actions.add('link')
                        if not self.parent.is_editable :
                            self.inactive_actions.add('link')

    @set_expander
    def detail(self):
        if not self.display_subclasses :
            return super(ListOfLink, self).detail()
        else :
            nodes = list()
            position = 0
            for subclass in self.subclasses :
                schema = get_schema(self.schema, subclass, self.record)
                constraint = get_constraint(schema)
                #update link properties for subclasses
                if self.link.reverse :
                    source = Field(subclass, self.link.source.name, self.link.source.verbose_name)
                    destination = Field(self.link.destination.klass, self.link.destination.name, subclass._meta.verbose_name)
                else :
                    source = Field(self.link.source.klass, self.link.source.name, subclass._meta.verbose_name)
                    destination = Field(subclass, self.link.destination.name, self.link.destination.verbose_name)
                link = Link(source, destination, self.link.type, self.link.reverse, self.link.required)
                #list with forced to single element
                #must be displayed as an ObjectLink
                is_fake = constraint and (constraint.max_objects < 2) and not (constraint.max_objects is None) and not isinstance(constraint, TableConstraint)
                if is_fake :
                    records = self.view.user.get_accessible(subclass.objects.all())
                    record = records.get() if records else None
                    if record :
                        _record = record.cast() if isinstance(record, Cast) else record
                        schema = get_schema(self.schema, subclass, _record)
                        node = ObjectLink(self.view, self, schema, link, _record, position, is_fake_object_link=True)
                    else :
                        node = SubclassNode(self.view, self, schema, link, self.record, self.key, subclass, position)
                else :
                    node = SubclassNode(self.view, self, schema, link, self.record, self.key, subclass, position)
                nodes.append(node)
                position += 1
        return nodes
    
    @property
    def _parent_node_type(self):
        return getattr(self.parent, 'node_type', None)
    
    @property
    def _parent_class_id(self):
        return getattr(self.parent.content_type, 'pk', None)
    
    @property
    def _parent_object_id(self):
        return getattr(self.parent.record, 'pk', None)
    
    @classmethod
    def get_parameters(cls):
        return [
            'class_id',
            'parent_node_type',
            'parent_class_id',
            'parent_object_id',
            'field',
            'reverse',
            'constraint_id',
            'subclass_id'
        ]

class SubclassNode(BaseListOfLink):
    """
    Subclass of BaseListOfLink, wrapping a database model
    that is the a subclass of its parent ListOfLink model.
    """
    
    def __init__(self, view, parent, schema, link, record, key, subclass, position, state=False):
        #find the model in the view node_models cache
        index = "%s_%s_subclassnode" % (parent.node_model_index, subclass._meta.verbose_name)
        if not index in view.node_models :
            model = SubclassNodeModel(subclass, schema, False, parent.node_type, view, key, link)
            view.node_models[index] = model
        else :
            model = view.node_models[index]
        super(SubclassNode, self).__init__(model, view, parent, schema, link, record, key, subclass, subclass._meta.verbose_name_plural, position, state)
        self.init_actions_to_display()
        self.value = None
    
    def init_actions_to_display(self):
        if ('add' in self.actions):
            if self.link.reverse :
                self.displayed_actions.add('add')
            elif "modify" in self.parent.parent.actions :
                self.displayed_actions.add('add')
                if not self.parent.parent.is_editable :
                    self.inactive_actions.add('add')
        #delete
        if 'delete' in self.actions :
            if self.link.reverse or 'modify' in self.parent.parent.actions :
                self.children_actions.add('delete')
        #modify
        if 'modify' in self.actions :
            if 'unlink' in self.actions and (self.link.reverse or 'modify' in self.parent.parent.actions) :
                self.children_actions.add('unlink')
            self.children_actions.add('modify')
        
        if 'link' in self.actions and 'modify' in self.actions :
            if self.link.reverse :
                self.displayed_actions.add('link')
            elif 'modify' in self.parent.parent.actions :
                self.displayed_actions.add('link')
                if not self.parent.parent.is_editable :
                    self.inactive_actions.add('link')

    def get_records(self):
        #if records are instances of UserPermission
        #then avoid displaying the permission relative to the user
        records = super(BaseListOfLink, self).get_records().cast(self.entity) 
#        if issubclass(self.entity, UserPermission) :
#            records = records.exclude(pk=records[0].pk)
        return records
    
    @property
    def _parent_class_id(self):
        return getattr(self.parent.parent.content_type, 'pk', None)
    
    @property
    def _parent_object_id(self):
        return getattr(self.parent.parent.record, 'pk', None)
    
    @classmethod
    def get_parameters(cls):
        return [
            'class_id',
            'parent_class_id',
            'parent_object_id',
            'field',
            'reverse',
            'constraint_id'
        ]

class View(object):
    
    def __init__(self, name, request=None):
        """
        Hierarchical structure of objects representing 
        a view on the database content that could be customized
        by templates and instances of models contained in the 
        'editor' application.
        """
        self.name = name
        self.states = SortedDict()
        self.order_by = SortedDict()
        self.ordering = SortedDict()
        self.pages = SortedDict()
        #some indexes to retrieve nodes from the view
        self.index = SortedDict()
        self.sections = SortedDict()
        self.classes = SortedDict()
        self.nodes = list()
        try :
            self.schema = DBView.objects.get(name=self.name)
        except :
            raise Exception("The specified '%s' view doesn't exist. Please launch the populate_editor command before." % (name))
        self.introspections = SortedDict()
        self.node_models = SortedDict()
        
        if request :
            self.user = User.objects.get(pk=request.user.pk)
            self.update_from_request(request)
        else :
            self.user = None #maybe replaced by an AnonymousUser later
        
        #introspection of all classes of the application
        self._introspect_all_classes()
        
        #pre-computation of base sections
        self._detail()
    
    def set_user(self, user):
        """Set the user attribute of the View."""
        self.user = User.objects.get(pk=user.pk)
    
    def detect_first_class_node(self):
        """Return the default selected class."""
        for index in self.classes.keyOrder :
            node = self.classes[index]
            if not node.displayed_in_navigator :
                order = self.classes.keyOrder.index(index)
                return self.classes[self.classes.keyOrder[order]] 
        
    def _introspect_all_classes(self):
        """Introspect all application classes."""
        classes = get_models()
        for cls in classes :
            self.introspections[cls] = SortedDict()
            #fields
            self.introspections[cls]['fields'] = regular_fields_objects(cls)
            self.introspections[cls]['fkeys'] = foreign_keys_objects(cls)
            self.introspections[cls]['ro2o'] = reverse_one_to_one_keys_objects(cls)
            self.introspections[cls]['m2m'] = many_to_many_fields_objects(cls)
            self.introspections[cls]['rfks'] = reverse_foreign_keys_objects(cls)
            self.introspections[cls]['rm2m'] = reverse_many_to_many_fields_objects(cls)
            self.introspections[cls]['grs'] = generic_relations_objects(cls)
            self.introspections[cls]['gfkeys'] = generic_foreign_keys_objects(cls)
            #subclasses
            self.introspections[cls]['subclasses'] = get_subclasses_recursively(cls, strict=False)
    
    def update_states(self, request):
        """Update for each node the last opening state."""
        self.states = request.session['views'][self.name]['states']
        
        #update sections states
        #the first base section is opened
        nodes = self.sections.values()
        first_section = nodes[0]
        for node in nodes :
            node._state = self.states.get(node.index, True if ((node == first_section) and node._expander) else node._expander)
            
        #update classes states
        for node in self.classes.values() :
            node._state = self.states.get(node.index, False)
            
    def update_ordering(self, request):
        """Update for each table the sort field and its relative ordering."""
        self.order_by = request.session['views'][self.name]['order_by']
        self.ordering = request.session['views'][self.name]['ordering']
                
        #update classes ordering
        nodes = [k for k in self.classes.values() if k.as_table]
        for node in nodes :  
            node.order_by = self.order_by.get(node.index, node.in_header[0][0])
            node.ordering = self.ordering.get(node.index, 'ascending')
    
    def update_pages(self, request):
        """Update for each paginated table the last viewed page number."""
        self.pages = request.session['views'][self.name]['pages']
        #update classes pages
        nodes = [k for k in self.classes.values() if k.as_table]
        for node in nodes :
            node.page = self.pages.get(node.index, 1)
    
    def update_selected_class(self, request):
        """Update the last selected class."""
        index = request.session['views'][self.name].get('selected_class_node', None)
        self.selected_class_node = self.classes[index] if index else self.detect_first_class_node()  
        
    def update_from_request(self, request):
        """Initialize internal states of the View from the specified request."""
        self.states.update(request.session['views'][self.name]['states'])
        self.order_by.update(request.session['views'][self.name]['order_by'])
        self.ordering.update(request.session['views'][self.name]['ordering'])
        self.pages.update(request.session['views'][self.name]['pages'])
        self.update_selected_class(request)
    
    def update_from_last_state(self, request):
        """Update internal states of the View from the specified request."""
        self.set_user(request.user)
        self.update_states(request)
        self.update_ordering(request)
        self.update_pages(request)
        self.update_selected_class(request)
    
    def _detail(self):
        """Create then cache base Section objects.""" 
        position = 0
        for schema in self.schema.children.all().cast(DBSection) :
            node = Section(self, None, schema, schema.title.title(), schema.position, state=not bool(position), is_root=True)
            self.nodes.append(node)    
            self.index[node.index] = node
            self.sections[node.index] = node
            position += 1
    
    def detail(self):
        """Return the list of base Section objects."""
        if not self.nodes :
            self._detail()
        return self.nodes

class ObjectView(object):
    """Placeholder to edit single object."""
    pass
