from copy import copy
from helmholtz.analysis.tools.core.analyses import Analysis
from helmholtz.analysis.tools.core.pins import Parameter,Input,DatabaseObject
from helmholtz.analysis.tools.managers.common import DBManager

#def configuration_match_component(view_func):
#    """Decorator that checks if a configuration is well suited to a component."""
#    def is_matching(self, configuration, manager=None, parallel=False):
#        assert isinstance(configuration, Configuration), "configuration must be an instance of Configuration"
#        attrs = dir(configuration)
#        comp_inputs = [k.name for k in self.get_inputs()]
#        inputs = [k for k in attrs if (k in comp_inputs)]
#        assert inputs.sort() == comp_inputs.sort(), "please put correct inputs into the configuration class"
#        configuration.list_of_inputs = inputs
#        return view_func(self, configuration, manager, parallel)      
#    is_matching.__doc__ = view_func.__doc__
#    return is_matching

def configuration_match_component(view_func):
    """Decorator that checks if input or parameter configuration is well suited to a component."""
    def is_matching(self,manager=None,parallel=False,**configuration):
        comp_inputs = [k.name for k in self.get_pins_of_type(Input)]
        pins = [k for k in configuration if (k in comp_inputs)]
        assert pins.sort() == comp_inputs.sort(), "please put correct inputs into the configuration class"
        return view_func(self,manager,parallel,**configuration)      
    is_matching.__doc__ = view_func.__doc__
    return is_matching

#def get_configuration_from_database(view_func):
#    """Decorator that get inputs value from the database."""
#    def get_data(self, **configuration):
#        if configuration.has_key("config_id") and configuration.has_key("manager") :
#            assert isinstance(manager,DBManager), "manager must be an instance of DBManager"
#            configuration = manager.get_configuration(self, configuration["config_id"])
#        return view_func(self, **configuration)
#    get_data.__doc__ = view_func.__doc__
#    return get_data

def replace_data_coming_from_database(view_func):
    def replace_data(self,manager=None,parallel=False,**configuration):
        assert isinstance(manager,DBManager) or (manager is None), "manager must be an instance of DBManager or None" 
        self.extern = dict()
        for key,item in configuration.items() :
            if isinstance(item,dict) and item.has_key('module') and item.has_key('class') and item.has_key('query') :
                assert manager != None,"as the configuration need a database access to retrieve some data from database, please give a DBManager"
                obj = manager.get_object(item['module'],item['class'],item['query'])
                if item.has_key('field') :
                    #here is a Potential_DatabaseValue
                    self.extern[key] = {'object':obj,'field':item['field']}
                    configuration[key] = getattr(obj,item['field'])     
                elif isinstance(getattr(self,key),DatabaseObject) :
                    #here is a Potential_DatabaseObject
                    configuration[key] = obj
        return view_func(self,manager,parallel,**configuration)
    replace_data.__doc__ = view_func.__doc__
    return replace_data

#def replace_data_coming_from_database(view_func):
#    def replace_data(self, manager=None, parallel=False, comments=False, **configuration):
#        #assert isinstance(configuration, Configuration), "configuration must be an instance of Configuration"
#        assert isinstance(manager, DBManager) or (manager is None), "manager must be an instance of DBManager or None" 
#        for input in configuration.list_of_inputs :
#            potential = getattr(configuration, input)
#            cls = potential.__class__.__name__
#            if cls != "Extern" :
#                configuration.__dict__.update({input : potential})
#                configuration.inputs.update({input : potential})
#            else :
#                assert manager, "manager must not be None when analysis contains 'Extern' attributes"
#                manager.extract_data(configuration, input, potential)
#        return view_func(self, configuration, manager, parallel)
#    replace_data.__doc__ = view_func.__doc__
#    return replace_data