""" 
Introduction :

This set of classes is the foundation of a component based framework useful to develop, persist and expose (via django website) complex analysis workflows. This module has been developped with in mind that the analysis conception could be done the same way as electronic circuit design in order to construct reusable, modular and parallel processes in few steps. It abstracts the program execution flow by designing base components that encapsulate inputs, outputs and specific processes and mixing them to make other components. 

This component based conception is a way to avoid cross concern problems because the code of each base component acts only on its members. Moreover, It simplifies the parallelisation of the code by deducing the process workflow from component combinations and then make the computation available in a multicore context. As the process workflow is abstracted, it is possible to store components and their results into a database system and to broadcast them to the scientific community.

How to :

The design workflow starts by creating base components inheriting from the BaseComponent class of the framework. The structure of this kind of component contains :

    1 - A set of members that are Input, Parameter or Output objects; the pins of the object
    2 - As BaseComponent, the author which has designed the component corresponding to a database username
    3 - The compute method that executes the code deducing Output objects from Input/Parameter objects

    Example :

        from component import BaseComponent
        
        class myProcess1(BaseComponent) :
            "My first base process"
            def __init__(self) :
                self.author = 'DBUserName'
                self.attr1 = Input(constraint=float, usecase='first input')
                self.attr2 = Input(constraint=str, usecase='second input')
                ...
                self.attrM = Input(constraint=integer, usecase='last input')
                ...
                self.attrN = Parameter(constraint=str, usecase='first parameter')
                ...
                self.attrQ = Output(constraint=float, usecase='first output')
                ...
                self.attrZ = Output(constraint=YourPythonObject, usecase='second and last output')
            
            def compute(self) :
                self.attrN = f(self.attr1.potential, self.attr2.potential ..., self.attrM.potential)
                ...
                self.attrZ = g(self.attr1.potential, self.attr2.potential ..., self.attrM.potential)
        
        NB : 
            1 - A docstring to explain the process
            2 - constraint parameter could be useful to detect incompatible components. Anyway this parameter could be None.
            3 - usecase parameter could be useful to explain the role of a specific Input or Output
            4 - an Input is a piece of information coming from another process and a Parameter is an hard coded one
 
When the set of base components is sufficient it is time to design Component objects using combination of this objects. Its structure is a little bit different from the BaseComponent one. It contains :
        
        1 - As BaseComponent, a docstring to explain the resulting process
        2 - As BaseComponent, the author which has designed the component
        3 - As BaseComponent, a set of members that are Input, Parameter or Output objects. But they are not declared into __init__.
        4 - A set of members that are BaseComponent or Component objects used to realise the computation
        5 - The "schema" member reflecting connections between Component and SubComponents pins
        
        Example :
        
            from component import Component
            from myProcesses import myProcess1, myProcess2
            
            class myComponent1(Component) :
                "My First Component class"
                author = 'DBUserName'
                attr1 = Input(constraint=float, usecase='first input')
                attr2 = Input(constraint=str, usecase='second input')
                ...
                attrG = Parameter(constraint=str, usecase='second input')
                ...
                attrM = Input(constraint=integer, usecase='last input')
                attrN = Output(constraint=float, usecase='first output')
                ...
                attrZ = Output(constraint=YourPythonObject, usecase='second and last output')
                
                process1 = myProcess1()
                process2 = myProcess2() 
                
                schema = [[attr1, process1.attr1],
                                  [attr2, process1.attr2],
                                  ...
                                  [process1.attrN, process2.attr1],
                                  ...,
                                  [process1.attrZ, process2.attrM],
                                  ...,
                                  [process2.attrZ, attrZ]]
        
        NB : As say in (2) it is possible to make Component objects not only from BaseComponent but also other Component objects.

Before launching the computation, it is necessary to configure inputs/parameters of the new Component object. This is done by creating an Analysis object that contains :

        1 - A docstring to explain the configuration and its purpose
        2 - The author which launch the computation corresponding to the username of the database
        3 - The mapping between values used into configuration and inputs/parameters of the component
        
        Example :
        
            class myConfiguration1(Analysis) :
                "Test analysis class"
                
                author = 'DBUserName'
                attr1 = 1.4
                ...
                attrG = Extern('ExistingAnalysis', 'output_name')
                ...
                attrZ = YourPythonObject(attr1=10, attr2='myModel')
        
        NB : Extern objects corresponding to data coming from an database source.

Now, it is possible to launch the computation as following :

    Example :
    
        from myComponents import myComponent1
        from myConfigurations import myConfiguration1
        from Component.db_manager import DjangoManager
        
        authenticate('tbrizzi', 'django2007', DjangoManager())
        component = myComponent1()
        analysis = myConfiguration1(component, myDBManager)
        analysis.launch(register=True, auto=True, parallel=False, snapshot=True)
    
    NB : The Analysis class is responsible of launching the computation corresponding to the component. When register is True, the component is stored into a databasevia the DBManager called myDBManager in the example. If auto is True, the registration take in charge subcomponents registration. If the subcomponents are already stored into database they are updated only if  the person launching the computation is same as the component designer. If they are some analyses using this component the registration is stopped. If snapshot is True, inputs and results of the computation is stored into a database via the DBManager. If the DBManager is not specified, DjangoManager is used by default. If parallel is True and python 2.6 multiprocessing module is available, the process is launched in multicore context.
    
It is also possible to make component and analyses from XML files :
    
    from factory import ComponentFactory, AnalysisFactory
    from Component.db_manager import DjangoManager

    def launch_analysis(model, configuration) :    
        compfactory = ComponentFactory(model)
        anfactory = AnalysisFactory(configuration)
        pipeline = compfactory.create_component()
        analysis = anfactory.create_analysis(pipeline)
        register, snapshot = analysis.launch()
        if register :
            print register
            if snapshot :
                print snapshot
    
    if __name__ == "__main__":
        authenticate('tbrizzi', 'django2007', DjangoManager())
        model = "file:///home/thierry/Benchmarks_Project/benchmarks/contrast_response_component_chisquare.xml"
        configuration = "file:///home/thierry/Benchmarks_Project/benchmarks/contrast_response_analysis_chisquare.xml"
        launch_analysis(model,configuration)

It is also possible to regenerate a component from one stored into a database and launch an analysis :

    from factory import RegisteredFactory, AnalysisFactory

    def launch_analysis(model, configuration) :    
        compfactory = RegisterFactory(model)
        anfactory = AnalysisFactory(configuration)
        pipeline = compfactory.create_component()
        analysis = anfactory.create_analysis(pipeline)
        register, snapshot = analysis.launch()
        if register :
            print register
            if snapshot :
                print snapshot
    
    if __name__ == "__main__":
        model = "myComponent1"
        configuration = "file:///home/thierry/Benchmarks_Project/benchmarks/contrast_response_analysis_chisquare.xml"
        launch_analysis(model,configuration)

"""
 
THREADING = False
from django.conf import settings

from helmholtz.core.loggers import default_logger

logging = default_logger(__name__)

if THREADING :
    from thread import *
    from threading import *

try :
    from multiprocessing import Process, Lock, Event, Pool, Manager, Value, Queue, Condition
    from multiprocessing.managers import BaseManager
    MULTIPROCESSING = True
except :
    logging.warning('Warning: Multiprocessing module not available. Please install python 2.6 to enable multicore processing.')
    MULTIPROCESSING = False

import sys 
from copy import deepcopy
from helmholtz.analysis.tools.core.pins import Pin, Input, Output, Parameter, DatabaseObject, DatabaseValue, DatabaseObjectParameter, DatabaseValueParameter
from helmholtz.analysis.tools.core.decorators import configuration_match_component, replace_data_coming_from_database
from helmholtz.analysis.tools.managers.common import DBManager

class BaseComponentInternal(object) :
    """Internal functions used by the class."""
    
    def description(self) :
        """Returns the documentation linked to the Component."""
        return self.__class__.__doc__
    
    def _type(self) :
        """Returns the type of the Component."""
        return  self.__class__.__name__
    type = property(_type)
    
    def is_base(self):
        return True if self.__class__.__base__.__name__ == 'BaseComponent' else False
    
    def n_components(self) :
        """Returns the number of Components."""
        return len(self.get_components())
    
    def n_subcomponents(self) :
        """Returns the number of SubComponents."""
        return len([k for k in self.get_components_recursively() if k != self])
    
    def n_inputs(self) :
        """Returns the number of inputs."""
        return len(self.get_inputs())
    
    def n_outputs(self) :
        """Returns the number of outputs."""
        return len(self.get_outputs())
    
    def n_pins(self) :
        """Returns the total number of underlying pins."""
        components = self.get_components() + [k for k in self.get_components_recursively() if k != self]
        return self.n_inputs() + self.n_outputs() + sum([len(k.get_pins()) for k in components])
    
    def n_connections(self) :
        """Returns the total number of connections done into the Component."""
        only = self.get_components_only(exclude=self)
        if 'schema' in dir(self) :
            only.append(self)
        schema = [k.schema for k in only]
        return sum([len(k) for k in schema])
    
    def convert_inputs(self, inputs) :
        """Transfomrs a dictionary were key are Input/Output names to a dictionary were key are Input/Output instances.""" 
        assert isinstance(inputs, dict), "Input data must be a dictionary."
        new_inputs = {}
        for input, value in inputs.items() :
            try :
                new_inputs[getattr(self, input)] = value
            except :
                raise Exception("Input %s does not exist." % (input))
        assert len(new_inputs) == len(self.get_inputs()), "Wrong number of inputs." 
        return new_inputs

    def power_on(self, inputs) :
        """Set component inputs to values contained into inputs dictionary."""
        for input, value in inputs.items() :
            input.potential = value
            for connection in input.connected_to :
                connection.potential = input.potential
    
    def propagate_inputs(self) :
        """Same as power_on but values coming from the component itself."""
        for input in self.get_inputs() :
            for connection in input.connected_to :
                connection.potential = input.potential
    
    def get_outputs(self) :
        """Returns list of tuples containing the name of an ouput and the corresponding Pin object."""
        return [pin for name, pin in self.__dict__.items() if isinstance(pin, Output)]
    
    def get_dict_of(self, pintype):
        """Return a dictionary of pins of specified type."""
        assert pintype in [Output, Input, Parameter], "pintype must be in [Input,Parameter,Output]"
        pins = {}
        items = [(name, pin.potential) for name, pin in self.__dict__.items() if isinstance(pin, pintype)]
        for item in items :
            pins.update({item[0]: item[1]}) 
        return pins
    
    def get_outputs_dict(self) :
        """Returns a dictionary with output name as key and its relative value."""
        outputs = {}
        items = [(name, pin.potential) for name, pin in self.__dict__.items() if isinstance(pin, Output)]
        for item in items :
            outputs.update({item[0]: item[1]}) 
        return outputs
    
    def get_parameters_dict(self):
        """Returns a dictionary with parameters name as key and its relative value."""
        parameters = {}
        items = [(name, pin.potential) for name, pin in self.__dict__.items() if isinstance(pin, Parameter)]
        for item in items :
            parameters.update({item[0]: item[1]}) 
        return parameters
    
    def get_inputs_dict(self) :
        """Returns a dictionary with output name as key and its relative value."""
        inputs = {}
        items = [(name, pin.potential) for name, pin in self.__dict__.items() if isinstance(pin, Input)]
        for item in items :
            inputs.update({item[0]: item[1]}) 
        return inputs
    
    def get_pins_of_type(self, pintype) :
        """Returns list of tuples containing the name of a specified pin type and the corresponding Pin object."""
        return [pin for name, pin in self.__dict__.items() if isinstance(pin, pintype)]
    
    def get_inputs(self) :
        """Returns list of tuples containing the name of an ouput and the corresponding Pin object."""
        return [pin for name, pin in self.__dict__.items() if isinstance(pin, Input)]
    
    def get_pins(self) :
        """Returns list of tuples containing the name of a pin and the corresponding Pin object."""
        return self.get_inputs() + self.get_outputs()
    
    def get_components(self) :
        """Returns list of tuples containing the name of a component and the corresponding Pin object."""
        components = [pin for name, pin in self.__dict__.items() if (isinstance(pin, BaseComponent) and (name != "component"))]
        return components
    
    def get_components_only(self, all=[], exclude=None, mainloop=True) :
        """Gets direct subcomponents included in the component."""
        if mainloop : all = []
        base = self.get_components()
        if exclude :
            base = [k for k in base if not isinstance(k, type(exclude))]
        for component in base :
            if isinstance(component, Component) :
                all.append(component)
                component.get_components_only(all, component.component, mainloop=False)
        if mainloop : 
            return all

    def get_components_recursively(self, all=[], exclude=None, mainloop=True) :
        """Gets recursively subcomponents included in the component."""
        if mainloop : all = []
        base = self.get_components()
        if exclude :
            base = [k for k in base if not isinstance(k, type(exclude))]
        for component in base :
            if isinstance(component, Component) :
                component.get_components_recursively(all, component.component, mainloop=False)
            elif isinstance(component, BaseComponent) :
                all.append(component)
        if mainloop :
            all.append(self) 
            return all
    
    def get_dependencies(self) :
        """Get all components necessary to realize the component computation."""
        inputs = self.get_inputs()
        components = []
        for input in inputs :
            for connection in input.connected_to :
                if 'component' not in dir(connection.component) :
                    components.append(connection.component)
                elif isinstance(connection, Output) or (isinstance(connection, Input) and (connection.component == self.component)) :
                    components.append(connection.component)
        return set(components)
    
    def propagate_potential(self) :
        """Propagate outputs of a component to other component inputs."""
        outputs = self.get_outputs_dict()
        for output, value in outputs.items() :
            for pin in getattr(self, output).connected_to :
                pin.potential = value

    def update_potential(self, pins):
        """Updates pins of a component from values computed into a thread."""
        for key, value in pins.items() :
            pin = getattr(self, key)
            pin.potential = value

    def is_input(self, pin) :
        """Test if a Pin object is an Input or an Output."""
        if isinstance(pin, Input) :
            return True
        elif isinstance(pin, Output) :
            return False

class BaseComponent(BaseComponentInternal) :
    """Take in charge the in memory and database representation of a Component (Input, Output objects) : 
    
    - name : (alias) of the component used in an other component.
    - component : the Component where the BaseComponent is used.
    
    user interface :
        - set_inputs(self, inputs) : to define component inputs.
        - register(self) : to store in the database via django ORM.
        - snapshot(self, id, intermediates, comments) : keep a trace of an analysis done with a component in the database via django ORM.
        - info(self) : description of the component (inputs, outputs, schema and used base component).
        - db_info(self) : description of the component from the database point of view, include same data as info(self) fuction, but all links to direct or indirect analyses done with the component. 
    
    """
    def __init__(self, inputs=None) :
        assert 'version' in dir(self), 'please specify the version number of the component.'
        #As in custom component one do not use __init__ 
        #the __dict__ does not contain object attributes 
        #It is necessary to put them dynamically in the object dictionary
        new_dct = dict()
        attrs = dir(self)
        for key in attrs :
            attribute = getattr(self, key)
            if isinstance(attribute, Pin) or isinstance(attribute, BaseComponent) or (key == 'schema') :
                new_dct[key] = attribute
        #deepcopy is here to authorize using the same subcomponent in a complex component
        #and avoid pointing to the same inputs/outputs in the memory        
        self.__dict__ = deepcopy(new_dct)        
        #detect the name and component of each input / output
        #after deepcopy in order to avoid deepcopy of links
        for key, attribute in self.__dict__.items() :
            if isinstance(attribute, Pin) or isinstance(attribute, BaseComponent) :
                attribute.name = key
                attribute.component = self   
        #set component attributes  
        self.name = None
        self.analysis = None
        self.extern = {}
        self.usecase = self.__class__.__doc__
        self.computed = False
        self.author = None 
        self.extra_parameters = None
                         
        if inputs :
            new_inputs = self.convert_inputs(inputs)
            self.power_on(new_inputs)
    
    def parallel_process(self, queue) :
        self.execute()
        queue.put(self.get_outputs_dict())
    
    def info(self) :
        """Display information concerning the model of a Component or BaseComponent"""
        print "\nComponent of type : %s\n" % self.type
        inputs = self.get_inputs()
        outputs = self.get_outputs()
        components = self.get_components()
        recursive_components = [k for k in self.get_components_recursively() if k != self]
        print "Number of Inputs : %s" % (self.n_inputs())
        print "Number of Outputs : %s" % (self.n_outputs())
        print "Number of Pins : %s" % (self.n_pins())
        print "Number of Components : %s" % (self.n_components())
        print "Number of SubComponents : %s" % (self.n_subcomponents())
        print "Number of Connections : %s" % (self.n_connections())
        print "\nInputs :"
        for input in  inputs :
            if input.constraint :
                print " - %s : usecase = %s ; constraint = %s" % (input.name, input.usecase, input.constraint.__name__)
            else :
                print " - %s : usecase = %s ; constraint = %s" % (input.name, input.usecase, input.constraint)
        print "\nOutputs :"
        for output in outputs :
            if output.constraint :
                print " - %s : usecase = %s ; constraint = %s" % (output.name, output.usecase, output.constraint.__name__)
            else :
                print " - %s : usecase = %s ; constraint = %s" % (output.name, input.usecase, output.constraint)
        if len(components) > 0 : 
            print "\nComponents :"
            for component in components :
                print " - %s as %s" % (component.type, component.name)   
        print "\nDescription :\n\n%s" % (self.description())
        if ('schema' in dir(self)) and (len(self.schema) > 0) :
            print "\nConnectivity :"
            filtered_schema = [k for k in self.schema if ((k[0].component == self) or (k[1].component == self))]
            for first, second in filtered_schema :
                print " - %s.%s ---> %s.%s" % (first.component.type, first.name, second.component.type, second.name)
    
    def register(self, manager, auto=False):
        assert isinstance(manager, DBManager), "manager must be an instance of DBManager"
        manager.register(self, auto=auto)
    
    def snapshot(self, manager, label, comments=None, permissions=None):
        assert isinstance(manager, DBManager), "manager must be an instance of DBManager"
        analysis = manager.snapshot(self, label, comments, permissions)
        return analysis
            
    def execute(self) :
        """This method must be overloaded by subclasses."""
        raise Exception("The compute function must be overloaded into subclasses.")
    
    def replace_database_objects(self):
        db_inputs = [k for k in self.get_pins() if (isinstance(k, DatabaseObject) or isinstance(k, DatabaseObjectParameter) or isinstance(k, DatabaseValue) or isinstance(k, DatabaseValueParameter))]
        for input in db_inputs :
            key = input.name
            if isinstance(self.analysis[key], input.constraint) :
                pass
            else :
                if isinstance(input, DatabaseObject) or isinstance(input, DatabaseObjectParameter) :
                    assert self.analysis[key].has_key('module') and self.analysis[key].has_key('class') and self.analysis[key].has_key('query'), "please specify 'module','class' and 'query' for a DatabaseObject" 
                elif isinstance(input, DatabaseValue) or isinstance(input, DatabaseValueParameter) :
                    assert self.analysis[key].has_key('module') and self.analysis[key].has_key('class') and self.analysis[key]['field'] and self.analysis[key].has_key('query'), "please specify 'module','class', 'field' and 'query' for a DatabaseValue" 
                obj = input.manager.get_object(self.analysis[key]['module'], self.analysis[key]['class'], **self.analysis[key]['query'])  
                if isinstance(input, DatabaseObject) or isinstance(input, DatabaseObjectParameter) :
                    self.analysis[key] = obj 
                elif isinstance(input, DatabaseValue) or isinstance(input, DatabaseValueParameter) :
                    input.object = obj
                    self.analysis[key] = getattr(obj, self.analysis[key]['field']) 
        return db_inputs
    
    def replace_extern_inputs(self, manager, db_inputs):
        for key, item in [(k, v) for k, v in self.analysis.items() if not k in db_inputs] :
            if isinstance(item, dict) and item.has_key('module') and item.has_key('class') and item.has_key('query') and item.has_key('field') :
                assert manager, 'please specify a manager'
                obj = manager.get_object(self.analysis[input.name]['module'], self.analysis[input.name]['class'], **self.analysis[input.name]['query']) 
                self.analysis[key] = getattr(obj, item['field'])  
                #must memorize object and field to perform a snapshot of a database value   
                self.extern[key] = {'object':obj, 'field':item['field']} 
            
    @configuration_match_component
    def process(self, manager=None, parallel=False, extra_parameters=None, **configuration) :
        """Compute the function realized by the combination of subcomponents included in the component."""
        assert isinstance(manager, DBManager) or (manager is None), "manager must be an instance of DBManager or None"
        if extra_parameters :
            self.extra_parameters = extra_parameters
        self.analysis = configuration 
        self.extern = dict()
        db_inputs = self.replace_database_objects()   
        self.replace_extern_inputs(manager, db_inputs)   
        new_inputs = self.convert_inputs(self.analysis)
        self.power_on(new_inputs)
        if isinstance(self, Component) :
            if not parallel :
                self.compute_in_serial()
            else :
                self.compute_processes()
        elif isinstance(self, BaseComponent) :
            self.execute()
    
class Component(BaseComponent) :
    """ Take in charge connections between all pins and the workflow corresponding to the schema:
    
    connections : a list of all Connection object computed from the schema
    workflow : a list of all stage of a computation 
    threads : list of threads attached to a workflow step
    start_event : top synchro to launch prepared threads on demand
    """
    
    def __init__(self, inputs=None) :
        super(Component, self).__init__(inputs=inputs)
        assert self.schema_is_valid(), "schema is not valid."
        self.connections = []
        self.replaced_connections = {}
        self.workflow = []
        self.threads = []
        self.start_event = None
        self.connect_pins()
    
    def update_structure(self, default) :
        for pin in default :
            pin_type = type(pin)
            self.__dict__.update({pin.name : pin_type(constraint=pin.constraint, usecase=pin.usecase)})
            pin_obj = getattr(self, pin.name)
            pin_obj.component = self
            pin_obj.name = pin.name
            pin_comp = getattr(pin.component, pin.name)
            self.schema.append([pin_obj, pin_comp])
            pin_obj.connected_to.append(pin_comp)
            pin_comp.connected_to.append(pin_obj)
    
    def get_default(self) :
        """Search for obvious disconnections""" 
        default = []
        components = [k for k in self.get_components() if k != self]
        all_components = self.get_components_recursively()
        for component in components :
            pins = component.get_pins()
            for pin in pins :
                if pin.connected_to < 1 :
                    default.append(pin)
                else :
                    subcomponents = [k for k in component.get_components_recursively() if (k != component)]
                    connections = [k for k in pin.connected_to if not (k.component in subcomponents)]
                    if not len(connections) :
                        default.append(pin)
        return default
    
    def connect_pins(self) :
        """Create an in memory representation of the specified schema."""
        for connection in self.schema :
            connection[0].connected_to.append(connection[1])
            connection[1].connected_to.append(connection[0])
    
    def schema_is_valid(self) :
        assert 'schema' in dir(self), "schema not specified"
        assert isinstance(self.schema, list), "schema must be a list."
        for connection in self.schema :
            assert isinstance(connection, list) and (len(connection) == 2), "elements of schema must be lists of length 2."
            assert connection[0].constraint is connection[1].constraint, "Cannot connect 2 pins of different constraints (%s of %s:%s, %s of %s:%s)" % (connection[0].name, connection[1].constraint)
        return True
    
    def find_indirect_connections(self, connection, components, all=[], exclude=None, mainloop=True) :
        if exclude :
            connections = [k for k in connection.connected_to if not isinstance(k.component, type(exclude))]
        else :
            connections = connection.connected_to
        for other_connection in connections :
            if (other_connection.component in components) or (other_connection.component == self) :
                all.append(other_connection)
            else :
                self.find_indirect_connections(other_connection, components, all, exclude=connection.component, mainloop=False)
        if mainloop : 
            return all
    
    def substitute_connections(self, components) :
        for component in components :
            pins = component.get_pins()
            for pin in component.get_pins() :
                disconnections = []
                new_connections = []
                for connection in pin.connected_to :
                    if (connection.component != pin.component) and (not (connection.component in components)) :
                        disconnections.append(connection)
                        self.replaced_connections[connection] = pin
                        #find recursively
                        indirects = self.find_indirect_connections(connection, components, all=[], exclude=pin.component)
                        new_connections.extend(indirects)
                pin.connected_to.extend(new_connections)
                pin.connected_to = [connection for connection  in pin.connected_to if (not connection in self.replaced_connections)]
    
    def generate_workflow(self) :
        """Generates the workflow that will be executed to realize the component function."""
        components = self.get_components_recursively()
        self.substitute_connections(components)
        dependencies = [[component, component.get_dependencies()] for component in components if component != self]
        starting_point = set([component for component, components in dependencies if ((len(components) == 1) and (self in components))])
        self.workflow.append([k for k in starting_point])
        starting_point = starting_point.union(set([self]))
        while sum([len(k) for k in self.workflow]) < len(dependencies) :
            following_point = set([component for component, components in dependencies if ((starting_point.issubset(components) or components.issubset(starting_point)) and (component not in starting_point))])
            self.workflow.append([k for k in following_point])
            starting_point = starting_point.union(following_point)
    
    def compute_in_serial(self) :
        """Launches the component workflow in serial mode."""
        logging.warning("--- Start serial computation ---")
        self.generate_workflow()
        self.propagate_inputs()
        for components in self.workflow :
            for component in components :
                component.execute()
                component.propagate_potential()
        for replaced in self.replaced_connections :
            replaced.potential = self.replaced_connections[replaced].potential
    
    def prepare_threads(self) :
        self.start_event = Event()
        atom_events = [Event() for i in range(len(self.workflow) + 1)]
        i = 0
        old_thread = None
        for components in self.workflow :
            self.threads.append(ParallelCode(components, old_thread, self.start_event))
            old_thread = self.threads[-1]
            old_thread.start()
            for component in components :
                old_thread.atom_threads.append(AtomCode(component, atom_events[i]))
                old_thread.atom_threads[-1].start()
            i += 1
 
    def compute_in_parallel(self) :
        self.start_event.set()
    
    def compute_processes(self):
        """Launches the component workflow in parallel mode if multiprocessing library is available."""
        if MULTIPROCESSING :
            logging.warning("--- Multiprocessing available : use parallel computation functions. ---")
            logging.warning("--- Start parallel computation ---")
            for components in self.workflow :
                queues = []
                threads = []
                #launch processes
                for process in components :
                    queues.append(Queue())
                    threads.append(Process(target=process.parallel_process, args=(queues[-1],)))
                    threads[-1].start()
                #a loop to ensure that all processes are finished before next workflow step
                i = 0
                for component in components :
                    threads[i].join()
                    outputs = queues[i].get()
                    component.update_potential(outputs)
                    i += 1
            
        else :
            logging.warning("--- Multiprocessing not available : use serial computation functions. ---")
            self.compute_in_serial()
        self.computed = True

    def prepare_processes(self) :
        self.start_event = Event()
        events = [Event() for i in range(len(self.workflow) + 1)]
        atom_events = [Event() for i in range(len(self.workflow) + 1)]
        i = 0        
        for components in self.workflow :
            print events[i]
            threads = []
            if i == 0 :
                threads.append(ParallelProcess(components, None, self.start_event, events[i]))
            else :
                threads.append(ParallelProcess(components, events[i - 1], self.start_event, events[i]))
            threads[-1].start()
            for component in components :
                threads[-1].atom_threads.append(AtomProcess(component, atom_events[i]))
                threads[-1].atom_threads[-1].start()
            i += 1
    
    def start_processes(self) :
        self.start_event.set()
    
    def launch_processes(self, processes):
        i = 0
        for components in self.workflow :
            j = 0
            for component in components :
                thread = processes[i][j]
                thread[0].start()
                j += 1
            
            j = 0
            for component in components :
                thread = processes[i][j]
                outputs = thread[1].get()
                component.update_potential(outputs)
                thread[0].join()
                j += 1
            i += 1           
    
    
    
if THREADING :
    class AtomCode(Thread) :
        
        def __init__(self, component, start_event) :
            super(AtomCode, self).__init__()
            self.component = component
            self.start_event = start_event
    
        def run(self) : 
            print "Prepare Atomic Thread : %s" % (self.getName())
            self.start_event.wait()
            #print "Start Atomic Thread : %s" %(self.getName())
            self.component.process()
    
    class ParallelCode(Thread) :
        
        def __init__(self, components, parent_thread, start_event) :
            super(ParallelCode, self).__init__()
            self.components = components
            self.parent_thread = parent_thread
            self.atom_threads = []
            self.start_event = start_event
        
        def can_follow(self) :
            can_follow = True
            for component in self.parent_thread.components :
                if not component.finished :
                    can_follow = False
                    break
            return can_follow
        
        def run(self) :
            print "Prepare Workflow Thread : %s" % (self.getName())
            self.start_event.wait()
            print "Start Workflow Thread : %s" % (self.getName())
            if self.parent_thread :
                self.parent_thread.join()
            for atom in self.atom_threads :
                atom.start_event.set()
            for atom in self.atom_threads :
                atom.join()

if MULTIPROCESSING :
    class AtomProcess(Process) :
        
        def __init__(self, component, start_event) :
            super(AtomProcess, self).__init__(None, None, component.name)
            self.component = component
            self.start_event = start_event
    
        def run(self) : 
            print "Prepare Atomic Thread : %s" % (self.component.name)
            self.start_event.wait()
            #print "Start Atomic Thread : %s" %(self.getName())
            self.component.process()
    
    class ParallelProcess(Process) :
        
        def __init__(self, components, parent_event, start_event, end_event) :
            super(ParallelProcess, self).__init__(None, None, args=(parent_event, start_event, end_event))
            self.atom_threads = []
            self.start_event = start_event
            self.parent_event = parent_event
            self.end_event = end_event
        
        def run(self) :
            print self._args
            parent_event = self._args[0]
            start_event = self._args[1]
            end_event = self._args[2]
            print "Prepare Workflow Thread : %s" % (self.get_name())
            self.start_event.wait()
            print "Start Workflow Thread : %s" % (self.get_name())
            print parent_event
            if parent_event :
                parent_event.wait()
            for atom in self.atom_threads :
                atom.start_event.set()
            for atom in self.atom_threads :
                atom.join()
            self.end_event.set()
            print self.parent_event
            print self.end_event
