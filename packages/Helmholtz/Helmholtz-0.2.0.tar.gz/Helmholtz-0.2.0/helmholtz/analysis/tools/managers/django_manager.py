#from helmholtz.core.shortcuts import create_default_access_control, remove_access_control, delete_access_control
from copy import deepcopy
from django.conf import settings
from django.utils.datastructures import SortedDict
from helmholtz.core.modules import get_model_class
from helmholtz.core.populate import Populate, Column
from helmholtz.units.fields import PhysicalQuantity 
from helmholtz.analysis.tools.core.pins import Input, Output, Parameter, FileOutput, DatabaseObject, DatabaseObjectParameter, DatabaseValue, DatabaseValueParameter
from helmholtz.analysis.tools.managers.common import DBManager
from helmholtz.analysis.models.configuration import Configuration
from helmholtz.analysis.models.component import Component
from helmholtz.analysis.models.analysis import Analysis
from helmholtz.analysis.models.pin import Pin
from helmholtz.analysis.models.potential import Potential, Potential_PhysicalQuantity, Potential_Integer, Potential_Float, Potential_Existing, Potential_String, Potential_Boolean, Potential_Time, Potential_DateTime, Potential_PythonObject, Potential_Date
try :
    import cPickle as pickle
except :
    import pickle
import base64

from helmholtz.core.loggers import default_logger

logging = default_logger(__name__)

class ComponentNotRegisteredException(Exception):
    pass

class PermissionValidator(object):
    
    def set_permissions(self, mapping, permissions):
        logging.info('set component permissions')
        self.validate_permissions(permissions)
        mapping.permissions = permissions
    
    def validate_permissions(self, permissions):
        pass

class ComponentRegistrator(object):
    """Class responsible of component registration.""" 
    def __init__(self):
        self.mapper = Populate()
        self.permission_validator = PermissionValidator()
        #django description of the component
        dct = SortedDict({'label':None, 'version':None, 'usecase':None, 'base':None, 'code':None, 'package':None })
        dct['language'] = {'name':None}
        dct['permissions'] = list()
        dct['pin_set'] = list()
        dct['is_main_component_of'] = list()
        dct['connection_set'] = list()
        #django description of a pin
        pin_dct = {'label':None, 'usecase':None, 'pintype':{'name':None}, 'codingtype':{'name':None}}
        #django description of a subcomponent
        subcomponent_dct = {'subcomponent':{'label':None, 'version':None}, 'alias':None}
        #django description on a connection
        connection_dct = {'pin_left':{'label':None, 'component':{'label':None, 'version':None}},
                          'pin_right':{'label':None, 'component':{'label':None, 'version':None}},
                          'alias_left':{'component':{'label':None, 'version':None}, 'subcomponent':{'label':None, 'version':None}, 'alias':None},
                          'alias_right':{'component':{'label':None, 'version':None}, 'subcomponent':{'label':None, 'version':None}, 'alias':None}
                          }
        self.mapping = Column(dct)
        self.pin_mapping = Column(pin_dct)
        self.subcomponent_mapping = Column(subcomponent_dct)
        self.connection_mapping = Column(connection_dct)
    
    def cleanup(self, component):
        """Remove all objects dependent of the component."""
        logging.warning("refreshing the existing component %s" % (component.type))
        component_obj, created = Component.objects.get_or_create(label=component.type, version=component.version)
        if not created :
            component_obj.cleanup()
    
    def set_component(self, mapping, component):
        """Set component properties."""
        logging.info('set component parameters')
        mapping.label = component.type
        mapping.version = component.version
        mapping.usecase = component.__class__.__doc__
        mapping.base = True if component.__class__.__base__.__name__ == 'BaseComponent' else False
        mapping.language.name = 'python'
        mapping.code = None#component.execute.__doc__
        mapping.package = component.__module__
    
    def set_pins(self, mapping, component):
        """Set component pins properties.""" 
        logging.info('set component pins')
        pins = component.get_pins()
        for pin in pins :
            pin_mapping = deepcopy(self.pin_mapping)
            pin_mapping.label = pin.name
            pin_mapping.usecase = pin.usecase
            pin_mapping.pintype.name = pin.type
            if not pin.constraint :
                pin_mapping.codingtype = None
            else :
                module = pin.constraint.__module__
                if module == '__builtin__' : 
                    pin_mapping.codingtype.name = pin.constraint.__name__
                else :
                    pin_mapping.codingtype.name = "%s.%s" % (module, pin.constraint.__name__)
            mapping.pin_set.append(pin_mapping)
    
    def set_subcomponents(self, mapping, component, permissions, auto):
        """Set subcomponents properties."""
        logging.info('set component subcomponents')
        subcomponents = component.get_components()
        for subcomponent in subcomponents :
            subcomponent_mapping = deepcopy(self.subcomponent_mapping)
            if not auto :
                try :
                    subcomponent_obj = Component.objects.get(label=subcomponent.type, version=subcomponent.version)
                    subcomponent_mapping.subcomponent.label = subcomponent_obj.name
                    subcomponent_mapping.subcomponent.version = subcomponent_obj.version
                    subcomponent_mapping.alias = subcomponent.name 
                except :
                    raise Exception('subcomponent %s not stored in database, please register it before.' % (subcomponent.type))
            else :
                subcomponent_mapping.subcomponent = self.set_mapping(subcomponent, permissions, auto)
                subcomponent_mapping.alias = subcomponent.name
            mapping.is_main_component_of.append(subcomponent_mapping)
                
    def set_connections(self, mapping, component):
        """Set connections to link components."""
        logging.info('set component connections')
        if 'schema' in dir(component):
            for connection in component.schema :
                connection_mapping = deepcopy(self.connection_mapping)
                connection_mapping.pin_left.label = connection[0].name
                connection_mapping.pin_left.component.label = connection[0].component.type
                connection_mapping.pin_left.component.version = connection[0].component.version
                connection_mapping.pin_right.label = connection[1].name
                connection_mapping.pin_right.component.label = connection[1].component.type
                connection_mapping.pin_right.component.version = connection[1].component.version
                if connection[0].component is component :
                    connection_mapping.alias_left = None
                else :
                    connection_mapping.alias_left.component.label = component.type
                    connection_mapping.alias_left.component.version = component.version
                    connection_mapping.alias_left.subcomponent.label = connection[0].component.type
                    connection_mapping.alias_left.subcomponent.version = connection[0].component.version
                    connection_mapping.alias_left.alias = connection[0].component.name
                if connection[1].component is component :
                    connection_mapping.alias_right = None
                else :
                    connection_mapping.alias_right.component.label = component.type
                    connection_mapping.alias_right.component.version = component.version
                    connection_mapping.alias_right.subcomponent.label = connection[1].component.type
                    connection_mapping.alias_right.subcomponent.version = connection[1].component.version
                    connection_mapping.alias_right.alias = connection[1].component.name
                mapping.connection_set.append(connection_mapping)
                
    def set_mapping(self, component, permissions, auto):
        """Set the mapping compatible with the database schema."""
        mapping = deepcopy(self.mapping)
        self.set_component(mapping, component)
        self.permission_validator.set_permissions(mapping, permissions)
        self.set_pins(mapping, component)
        self.set_subcomponents(mapping, component, permissions, auto)
        self.set_connections(mapping, component)
        logging.info('%s' % (mapping.dictionarize()))
        return mapping
            
    def register(self, component, permissions=None, auto=False):
        """Launch registration of the component into the database."""
        mapping = self.set_mapping(component, permissions, auto)
        component_obj = self.mapper.store(Component, [mapping])
        return component_obj[0]

class AnalysisRegistrator(object):
    """Class responsible of analyses registration."""
    
    def __init__(self):
        self.mapper = Populate()
        self.permission_validator = PermissionValidator()
        #django description of the component
        dct = SortedDict({'force':True,
                          'label':None,
                          'comments':None,
                          'component':{'label':None, 'version':None},
                          'configuration':{'pk':None}
                         })
        dct['inputs'] = list()
        dct['outputs'] = list()
        dct['permissions'] = list()
        self.mapping = Column(dct)
    
    def set_analysis(self, mapping, component, label, comments):
        """Set analysis properties."""
        logging.info('set analysis parameters')
        mapping.label = label
        mapping.component.label = component.type
        mapping.component.version = component.version
        mapping.comments = comments
    
    def set_potentials(self, mapping, component):
        pins = component.get_pins()
        parameters = list()
        configurations = list()
        for pin in pins :
            value = pin.potential
            if isinstance(pin, DatabaseObject) :
                class_name = 'potential_databaseobject_id' if isinstance(value.pk, int) else 'potential_databaseobject_name'
                potential_mapping = Column({'force':True,
                                            class_name:{'value':{'__target_class__':value.__class__.__name__, 'pk':value.pk}},
                                            'pin':{'label':pin.name,
                                                   'component':{'label':component.type,
                                                                'version':component.version}}})
            elif isinstance(pin, DatabaseValue) :
                class_name = 'potential_databasevalue_id' if isinstance(pin.object.pk, int) else 'potential_databaseobject_name'
                potential_mapping = Column({'force':True,
                                            class_name:{'value':{'__target_class__':pin.object.__class__.__name__, 'pk':pin.object.pk},
                                                        'field':pin.field},
                                            'pin':{'label':pin.name,
                                                   'component':{'label':component.type,
                                                                'version':component.version}}})
            elif isinstance(pin, Input) and component.extern.has_key(pin.name) :
                obj = component.extern[pin.name]['object']
                field = component.extern[pin.name].get('field', None)
                if not field :
                    class_name = 'potential_databaseobject_id' if isinstance(obj.pk, int) else 'potential_databaseobject_name' 
                else :
                    class_name = 'potential_databasevalue_id' if isinstance(obj.pk, int) else 'potential_databasevalue_name'
                potential_mapping = {'force':True,
                                     class_name:{'value':{'__target_class__':obj.__class__.__name__,
                                                          'pk':obj.pk},
                                     'pin':{'label':pin.name,
                                            'component':{'label':component.type,
                                                         'version':component.version}}}}
                if not component.extern[pin.name].has_key('field') :
                    potential_mapping[class_name]['field'] = component.extern[pin.name]['field']
                potential_mapping = Column(potential_mapping)
            elif isinstance(pin, FileOutput) :
                split_path = pin.potential.value.split('/')
                split_filename = split_path[-1].split('.')
                mimetype = split_filename[-1]
                filename = '.'.join(split_filename[0:-1])
                if min.potential.root :
                    location = '/'.join(split_path[0:-1]).replace(pin.potential.root, '')
                potential_mapping = Column({'force':True,
                                            'potential_file':{'value':{'name':filename,
                                                                       'original':False,
                                                                       'mimetype':{'extension':mimetype,
                                                                                   'name':'application/octet-stream'},
                                                                       'filesystem':{'root':pin.potential.root,
                                                                                     'location':location}}},
                                            'pin':{'label':pin.name,
                                                   'component':{'label':component.type,
                                                                'version':component.version}}})
            else :
                #force the value to be compatible with the constraint
                type_test = pin.constraint if pin.constraint else type(value)   
                 
                if issubclass(type_test, int) :
                    class_name = 'potential_integer' 
                elif issubclass(type_test, float) :
                    class_name = 'potential_float'
                elif issubclass(type_test, basestring) :
                    class_name = 'potential_string'
                elif issubclass(type_test, bool) :
                    class_name = 'potential_boolean'
                elif issubclass(type_test, PhysicalQuantity) :
                    class_name = 'potential_physicalquantity'
                    value = {'value':value.value, 'unit':{'name':value.unit}}
                else :
                    class_name = 'potential_pythonobject'
                    value = pickle.dumps(value)
                potential_mapping = Column({'force':True,
                                            class_name:{'value':value},
                                            'pin':{'label':pin.name,
                                                   'component':{'label':component.type,
                                                                'version':component.version}}})
            if isinstance(pin, Input) and not isinstance(pin, Parameter):
                mapping.inputs.append(potential_mapping)
            elif isinstance(pin, Output) :
                mapping.outputs.append(potential_mapping)
            elif isinstance(pin, Parameter) :
                parameter_mapping = {'pin__label':pin.name,
                                     'pin__component__label':component.type,
                                     'pin__component__version':component.version,
                                     'pin__pintype__name':pin.type,
                                     'config_of__isnull':False
                                    }
                potentials = Potential.objects.filter(**parameter_mapping)
                if potentials :
                    configurations.append(set([k.config_of.all()[0].pk for k in potentials]))
                to_create = deepcopy(parameter_mapping)
                to_create.pop('config_of__isnull')
                #detect subclass of Potential from the constraint
                type_test = pin.constraint if pin.constraint else type(value) 
                if issubclass(type_test, int) :
                    cls = Potential_Integer 
                elif issubclass(type_test, float) :
                    cls = Potential_Float
                elif issubclass(type_test, basestring) :
                    cls = Potential_String
                elif issubclass(type_test, bool) :
                    cls = Potential_Boolean
                elif issubclass(type_test, PhysicalQuantity) :
                    cls = Potential_PhysicalQuantity
                    value = {'value':value.value, 'unit':{'name':value.unit}}
                else :
                    cls = Potential_PythonObject
                    value = pickle.dumps(value)
                to_create['class'] = cls
                to_create['value'] = value
                parameters.append(to_create)        
        if parameters :
            self.init_configuration_id(mapping, component, parameters, configurations)
        
    def init_configuration_id(self, mapping, component, parameters, configurations):
        """Detect if a combination of parameters already exists. 
        Else create the configuration and its relative potentials.
        """
        if not configurations :
            self.create_new_configuration(mapping, component, parameters)
        else :
            intersection = self.intersect_configurations(configurations)
            if not intersection : 
                self.create_new_configuration(mapping, component, parameters)
            else :
                mapping.configuration.pk = list(intersection)[0]
    
    def intersect_configurations(self, configurations):
        """Detect the configuration id from the intersection of all configurations relative to a potential.""" 
        new_set = configurations[0]
        for configuration in configurations[1:] :
            new_set.intersection_update(configuration)
        assert len(new_set) in [0, 1], "problem with configuration"
        return new_set
    
    def create_new_configuration(self, mapping, component, parameters):
        potentials = self.create_potentials(parameters)
        configuration = self.create_configuration(component, potentials)
        mapping.configuration.pk = configuration.pk
    
    def create_configuration(self, component, potentials):
        component_obj = Component.objects.get(label=component.type, version=component.version)
        configuration = Configuration.objects.create(component=component_obj)
        configuration.potentials.add(*potentials)
        return configuration
                
    def create_potentials(self, potentials):
        potential_obj = list()
        for potential in potentials :
            cls = potential['class']
            pin = Pin.objects.get(label=potential['pin__label'], pintype__name=potential['pin__pintype__name'],
                                  component__label=potential['pin__component__label'], component__version=potential['pin__component__version'])
            potential = cls.objects.create(pin=pin, value=potential['value'])
            potential_obj.append(potential)
        return potential_obj    
    
    def set_mapping(self, component, label, comments, permissions):
        mapping = deepcopy(self.mapping)
        self.permission_validator.set_permissions(mapping, permissions)
        self.set_analysis(mapping, component, label, comments)
        self.set_potentials(mapping, component)
        return mapping
    
    def snapshot(self, component, label=None, comments=None, permissions=None):
        try :
            Component.objects.get(label=component.type, version=component.version)
        except :
            raise ComponentNotRegisteredException('please register the component corresponding to the analysis before')
        mapping = self.set_mapping(component, label, comments, permissions)
        analysis_obj = self.mapper.store(Analysis, [mapping])
        return analysis_obj[0]
        
class DjangoServerManager(DBManager):
    
    def __init__(self):
        self.component_registrator = ComponentRegistrator()
        self.analysis_registrator = AnalysisRegistrator()
    
    def get_object(self, module_name, class_name, **query):
        entity = get_model_class(module_name, class_name)
        obj = entity.objects.get(**query)
        return obj
        
    def register(self, component, permissions=None, auto=False):
        self.component_registrator.register(component, permissions, auto)
    
    def snapshot(self, component, label, comments=None, permissions=None):
        self.analysis_registrator.snapshot(component, label, comments, permissions)
