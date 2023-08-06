# encoding: utf-8
from copy import deepcopy
from django.conf import settings
from django.utils.datastructures import SortedDict
from helmholtz.analysis.models.component import Component, SubComponent
from helmholtz.analysis.models.pin import Pin as ComponentPin
from helmholtz.analysis.models.analysis import Analysis
from helmholtz.analysis.models.configuration import Configuration
from helmholtz.analysis.tools.core.analyses import Analysis as AnConfig, Extern
from helmholtz.analysis.tools.core.pins import Pin, Input, Parameter, Output#,Debug
from helmholtz.analysis.tools.core.components import BaseComponent as BaseComp, Component as Comp
from helmholtz.analysis.tools.managers.django_manager import DjangoServerManager as Manager
#from base64 import last
#from helmholtz.analysis.tools.library.base_components.multiplier import Multiplier, Multipliers
from helmholtz.core.loggers import default_logger

logging = default_logger(__name__)

import unittest
from random import randint, choice

n_inputs = 5#randint(5,10)
n_outputs = 3#randint(5,10)
n_analyses = 5#randint(1,25)
n_subanalyses = 5#randint(1,25)
n_subsubanalyses = 5 #randint(10,25)
n_recurs = 5#randint(5,10) 
n_branches = 5#randint(5,10)

Analysis.objects.all().delete()
Component.objects.all().delete()
#ComponentPin.objects.all().delete()
#AccessControl.objects.all().delete()

def execute(self):
    inputs = self.get_inputs()
    for output in self.get_outputs():
        choices = []
        n_products = randint(1, len(inputs) - 1)
        for product in xrange(0, n_products + 1) :
            while (len(set(choices)) < n_products):
                choices.append(choice(inputs))
        output.potential = 1
        for ch in choices :
            output.potential *= ch.potential
        if output.potential > 1000000 :
            output.potential = 1000000

def set_analyses_tree():
    pass



class BaseComponentRegistrationTestCase(unittest.TestCase):
    
    def setUp(self):
        """Create components, analyses or other objects useful for all the testcase."""
        global n_inputs, n_outputs, n_analyses, n_subanalyses, n_subsubanalyses, n_recurs 
        attrs_comp = {'version':1, 'execute':execute, '__doc__':"a component generated randomly for test purpose"}
        attrs_comp_alt = {'version':1, 'execute':execute, '__doc__':"an alternative component generated randomly to test component re-registration"}
        attrs_an = {'id':'Config1', '__doc__':"the first configuration of the test component"}
        attrs_an_alt = {'id':'Config2', '__doc__':"the second configuration of the alternative component"}
        for n in xrange(0, n_inputs + 1) :
            attrs_comp.update({'input%s' % (n):Input(constraint=int, usecase='input%s' % (n))})
            attrs_an.update({'input%s' % (n):randint(1, 5)})    
            attrs_comp_alt.update({'input%s' % (n):Input(constraint=int, usecase='input%s' % (n))})
            attrs_an_alt.update({'input%s' % (n):randint(1, 5)})  
        for n in xrange(0, n_outputs + 1) :
            attrs_comp.update({'output%s' % (n):Output(constraint=int, usecase='output%s' % (n))})
            attrs_comp_alt.update({'output%s' % (n):Output(constraint=int, usecase='output%s' % (n))})
        Multiplier = type('Multiplier', (BaseComp,), attrs_comp)
        self.component = Multiplier()
        self.manager = Manager()
    
    def base_component_registration_test(self, component):
        """Test if a component is well registered.
        
        NB :
        
            1 - Verify if the Component instance relative to the component contains good label,usecase,base,package attributes
            2 - Verify if the component and its relative Component instance have the same number of pins
            3 - Verify if each component pin have a relative Pin instance containing good label,usecase,coding and type attributes
        
        """  
        #test component
        is_base = component.is_base()
        component_obj = None
        try :
            component_obj = Component.objects.get(label=component.type, version=component.version)
        except:
            self.assert_(component_obj, 'cannot find the component with label %s and version %s' % (component.type, component.version))
        self.assert_(component_obj.usecase == component.__doc__, 'component usecase not well stored')
        self.assert_(component_obj.base == is_base, 'component base not well stored')
        self.assert_(component_obj.package == component.__module__, 'component module not well stored')
        #test pins
        pins = component.get_pins()
        pins_obj = component_obj.pin_set.all()
        self.assert_(not(len(pins) > len(pins_obj)), "not all pins have been registered")
        self.assert_(not(len(pins) < len(pins_obj)), "too many pins have been registered")
        for pin in pins :
            pin_obj = pins_obj.get(label=pin.name)
            self.assert_(pin_obj.usecase == pin.usecase, "pin %s usecase not well stored : %s != %s" % (pin.name, pin_obj.usecase, pin.usecase)) 
            self.assert_(pin_obj.codingtype.name == pin.constraint.__name__, "pin %s coding not well stored : %s != %s" % (pin.name, pin_obj.codingtype.name, pin.constraint.__name__)) 
            self.assert_(pin_obj.pintype.name == pin.type, "pin %s type not well stored : %s != %s" % (pin.name, pin_obj.pintype.name, pin.type)) 
        
    def test_component_registration(self):
        """Test if a component is well registered.
        
        NB :
        
            1 - Verify if the Component instance relative to the component contains good label,usecase,base,package attributes
            2 - Verify if the component and its relative Component instance have the same number of pins
            3 - Verify if each component pin have a relative Pin instance containing good label,usecase,coding and type attributes
        
        """
        self.component.register(manager=self.manager)
        self.base_component_registration_test(self.component)

class ComplexComponentRegistrationTestCase(BaseComponentRegistrationTestCase):
    
    def setUp(self):
        #base component properties
        attrs_base = {'version':1, 'execute':execute, '__doc__':"a component that multiply two integer inputs"}
        for n in [1, 2] :
            attrs_base.update({'input%s' % (n):Input(constraint=int, usecase='input%s' % (n))}) 
        attrs_base.update({'output':Output(constraint=int, usecase='output')})
        BaseMultiplier = type('BaseMultiplier', (BaseComp,), attrs_base)
        #complex component properties
        attrs_complex = {'version':1, '__doc__':"a component generated randomly for test purpose"}
        n_levels = 3
        levels = [2 ** k for k in range(0, n_levels)]
        levels.reverse()
        n_inputs = 2 * levels[0]
        for n in range(1, n_inputs + 1) :
            attrs_complex.update({'input%s' % (n):Input(constraint=int, usecase='input%s' % (n))})    
        attrs_complex.update({'output':Output(constraint=int, usecase='output')})
        #creation of subcomponents
        for level in levels :
            index = levels.index(level)
            for n in range(1, level + 1) : 
                attrs_complex.update({'multiplier_%s%s' % (index + 1, n) : BaseMultiplier()})
        attrs_complex['schema'] = []
        #creation of schema
        input_index = 1
        level_index = 0
        for level in levels :
            index = levels.index(level)
            for n in range(1, level + 1) :
                name = 'multiplier_%s%s' % (index + 1, n)
                subcomponent = attrs_complex[name]
                if level == levels[0] :
                    #connect component outputs to subcomponent inputs
                    inputs = subcomponent.get_inputs()
                    inputs.sort(key=lambda x:x.name)
                    for subcomponent_input in inputs :
                        component_input = attrs_complex['input%s' % (input_index)]
                        connection = [component_input, subcomponent_input]
                        attrs_complex['schema'].append(connection)
                        logging.header('component.input%s -> %s.%s' % (input_index, name, subcomponent_input.name))
                        input_index += 1
                subcomponent_output = getattr(subcomponent, 'output')
                if level == levels[-1] :
                    #connect last subcomponent output to component output
                    component_output = attrs_complex['output']
                    connection = [subcomponent_output, component_output]
                    attrs_complex['schema'].append(connection)    
                    logging.header('%s.output -> component.output' % (name)) 
                else :
                    #connect subcomponent inputs to subcomponent preeceeding ouput
                    next_index = index + 1 
                    next_level = levels[next_index]
                    for k in range(1, next_level + 1) :
                        next_name = 'multiplier_%s%s' % (next_index + 1, k)
                        next_subcomponent = attrs_complex[next_name]
                        inputs = next_subcomponent.get_inputs()
                        inputs.sort(key=lambda x:x.name)
                        connected = False
                        for input in inputs :
                            connection = [subcomponent_output, input]
                            already_connected = [k[1] for k in attrs_complex['schema'] if (k[1] == input)]
                            if not already_connected :
                                attrs_complex['schema'].append(connection) 
                                logging.header('%s.output -> %s.%s' % (name, next_name, input.name))
                                connected = True  
                                break 
                        if connected :
                            break
            level_index += 1            
        ComplexMultiplier = type('ComplexMultiplier', (Comp,), attrs_complex)
        self.component = ComplexMultiplier()
        self.manager = Manager()
    
    def complex_component_registration_test(self, component):
        self.base_component_registration_test(component)
        subcomponents = component.get_components()
        for subcomponent in  subcomponents :
            if subcomponent.is_base() :
                self.base_component_registration_test(subcomponent)
            else :
                self.complex_component_registration_test(subcomponent)    
        component_obj = Component.objects.get(label=component.type)
        self.assert_(component_obj.is_main_component_of.count() == len(subcomponents), 'subcomponents have not been all registered')
        subcomponent_set = component_obj.is_main_component_of.all()
        for subcomponent in subcomponents :
            subcomponent_obj = subcomponent_set.get(alias=subcomponent.name, subcomponent__label=subcomponent.type)
        
        self.assert_(component_obj.connection_set.count() == len(component.schema), 'connections have not been all registered')
        connection_set = component_obj.connection_set.all()
        schema_length = len(component.schema)
        n_connections = connection_set.count()
        self.assert_(n_connections == schema_length, 'connection lengths are not equal : %s != %s' % (n_connections, schema_length))
        for connection in component.schema :
            kwargs = dict() 
            if connection[0].component is component :
                kwargs['alias_left'] = None
            else :
                kwargs['alias_left__component__label'] = component.type
                kwargs['alias_left__component__version'] = component.version
                kwargs['alias_left__subcomponent__label'] = connection[0].component.type
                kwargs['alias_left__subcomponent__version'] = connection[0].component.version
                kwargs['alias_left__alias'] = connection[0].component.name
            if connection[1].component is component :
                kwargs['alias_right'] = None
            else :
                kwargs['alias_right__component__label'] = component.type
                kwargs['alias_right__component__version'] = component.version
                kwargs['alias_right__subcomponent__label'] = connection[1].component.type
                kwargs['alias_right__subcomponent__version'] = connection[1].component.version
                kwargs['alias_right__alias'] = connection[1].component.name
            connection_obj = connection_set.filter(pin_left__label=connection[0].name,
                                                   pin_right__label=connection[1].name,
                                                   pin_left__component__label=connection[0].component.type,
                                                   pin_left__component__version=connection[0].component.version,
                                                   pin_right__component__label=connection[1].component.type,
                                                   pin_right__component__version=connection[1].component.version,
                                                   **kwargs)
            self.assert_(connection_obj.count() > 0, 'cannot find the connection')
            self.assert_(connection_obj.count() == 1, 'too many connections found')
                
    def test_component_registration(self):
        """Test if a complex component is well registered.
        
        NB :
        
            1 - Verify if the Component instance relative to the component contains good label,usecase,base,package attributes
            2 - Verify if the component and its relative Component instance have the same number of pins
            3 - Verify if each component pin have a relative Pin instance containing good label,usecase,coding and type attributes
        
        """
        self.component.register(manager=self.manager, auto=True)
        self.complex_component_registration_test(self.component)
        #Config1 = type('Config1', (Configuration,), attrs_an)
#        AltMultiplier = type('AltMultiplier',(BaseComp,),attrs_comp_alt)
        #Config2 = type('Config2', (Configuration,), attrs_an_alt)
        
#        self.analysis1 = deepcopy(attrs_an)
#        self.multiplier_alt = AltMultiplier()
#        self.analysis2 = deepcopy(attrs_an_alt)
#        self.components = []
#        self.configurations = []
#        self.components_alt = []
#        self.configurations_alt = []
#        #create analyses tree linked to multiplier, analysis1 and alternative multiplier and analysis2
#        for branch in xrange(0,n_branches+1) :
#            old_conf = deepcopy(attrs_an)
#            old_conf_alt = deepcopy(attrs_an_alt)
#            for analysis in xrange(0,n_subanalyses+1) :
#                new_attrs_comp = {'__doc__':"branch %s, subanalysis %s" % (branch,analysis),'execute':execute}
#                new_attrs_an = {'__doc__':"branch %s, subanalysis %s" % (branch,analysis)}
#                new_attrs_comp_alt = {'__doc__':"branch %s, subanalysis %s" % (branch,analysis),'execute':execute}
#                new_attrs_an_alt = {'__doc__':"branch %s, subanalysis %s" % (branch,analysis)}
#                for n in xrange(0,n_inputs+1) :
#                    new_attrs_comp.update({'input%s'%(n):Input(constraint=int,usecase='input%s' % (n))})
#                    new_attrs_an.update({'input%s'%(n):randint(1,5)})    
#                    new_attrs_comp_alt.update({'input%s'%(n):Input(constraint=int,usecase='input%s' % (n))})
#                    new_attrs_an_alt.update({'input%s'%(n):randint(1,5)})    
#                for n in xrange(0,n_outputs+1) :
#                    new_attrs_comp.update({'output%s'%(n):Output(constraint=int,usecase='output%s' % (n))})
#                    new_attrs_comp_alt.update({'output%s'%(n):Output(constraint=int,usecase='output%s' % (n))})
#                
#                new_comp = type('Multiplier_%s_%s' % (branch,analysis),(BaseComp,),new_attrs_comp)
#                selected_output = 'output%s' % (choice(xrange(0,n_outputs+1)))
#                new_attrs_an['input%s' % (choice(xrange(0,n_inputs+1)))] = (old_conf['id'],selected_output) 
#                #new_conf = type('Config_%s_%s' % (branch, analysis), (Configuration,),new_attrs_an)
#                new_conf = deepcopy(new_attrs_an)
#                new_conf['id'] = 'Config_%s_%s' % (branch,analysis)
#                self.components.append(new_comp())
#                self.configurations.append(new_conf)
#                old_conf = new_conf
#                
#                new_comp_alt = type('AltMultiplier_%s_%s' % (branch, analysis), (BaseComp,), new_attrs_comp_alt)
#                selected_output = 'output%s' % (choice(xrange(0,n_outputs+1)))
#                new_attrs_an_alt['input%s' % (choice(xrange(0,n_inputs+1)))] = (old_conf_alt['id'],selected_output) 
#                #new_conf_alt = type('AltConfig_%s_%s' % (branch, analysis), (Configuration,), new_attrs_an_alt)
#                new_conf_alt = deepcopy(new_attrs_an_alt)
#                new_conf_alt['id'] = 'AltConfig_%s_%s' % (branch,analysis)
#                self.components_alt.append(new_comp_alt())
#                self.configurations_alt.append(new_conf_alt)
#                old_conf_alt = new_conf_alt
                
            
        
        
        #create analyses depending on the first one
#        for n in xrange(0,n_subanalyses+1) :
#            attrs_comp = {'execute':execute, '__doc__':"a component generated randomly for test purpose"}
#            attrs_sub = {'__doc__':"sub configuration %s of Config1" % (n)}
#            for m in xrange(0,n_inputs+1) :
#                attrs_comp.update({'input%s'%(m):Parameter(constraint=int, usecase='input%s' % (m))})
#                #attrs_sub.update({'input%s'%(m):randint(1, 5)}) 
#                link = randint(0,1)
#                if link :
#                    choices = [k for k in self.configurations]
#                    #choices.extend(2*[self.configurations.items()[0][0]])
#                    config = choice(choices)
#                    output_numbers = xrange(0,n_outputs+1)
#                    output = 'output%s' % (choice(output_numbers))
#                    attrs_sub.update({'input%s' % (m):Extern(self.configurations[config].__class__.__name__, output)})
#                else :
#                    attrs_sub.update({'input%s' % (m):randint(1,5)})
#            for m in xrange(0,n_outputs+1) :
#                attrs_comp.update({'output%s'%(m):Output(constraint=int, usecase='output%s' % (m))})
#            NewMultiplier = type('NewMultiplier%s'%(n), (BaseComp,), attrs_comp)
#            NewConfig = type('NewConfiguration%s' % (n), (Configuration,), attrs_sub)
#            self.configurations.update({'configuration%s' % (n+1):NewConfig()})
#            self.components.update({'components%s' % (n+1):NewMultiplier()})
        #create analyses depending on other analyses
#        for n in xrange(0,n_subsubanalyses+1) :
#            attrs_sub = {'__doc__':"sub sub configuration %s" % (n+n_subanalyses+1)}
#            for m in xrange(0,n_inputs+1) :
#                link = randint(0,1)
#                if link :
#                    config = choice([k for k in self.configurations])
#                    output_numbers = xrange(0,n_outputs+1)
#                    output = 'output%s' % (choice(output_numbers))
#                    attrs_sub.update({'input%s' % (m):Extern(self.configurations[config].__class__.__name__, output)})
#                else :
#                    attrs_sub.update({'input%s' % (m):randint(1,5)})
#            Config = type('Configuration%s' % (n+n_subanalyses+1), (Configuration,), attrs_sub)
#            self.configurations.update({'configuration%s' % (n+n_subanalyses+1):Config()})             
#        self.manager = Manager()
    
    
        
#    def test_2_analysis_registration(self):
#        """See if an analysis is well registered.
#        
#        NB :
#        
#            1 - Verify that each potential of a launched component has got a relative Potential instance  
#            2 - Verify that potential and its relative Potential instance share the same value 
#            3 - Verify if potential deriving
#        
#        """
#        ids = []
#        comments = []
#        self.multiplier.register(manager=self.manager)
#        ids.append(self.analysis1.pop('id')) 
#        comments.append(self.analysis1.pop('__doc__'))
#        self.multiplier.process(**self.analysis1)
#        self.multiplier.snapshot(self.manager,ids[0],comments[0])
#        n = 0
#        for component in self.components :
#            component.register(manager=self.manager)
#            ids.append(self.configurations[n].pop('id'))
#            comments.append(self.configurations[n].pop('__doc__'))
#            component.process(manager=self.manager,**self.configurations[n])
#            component.snapshot(self.manager,ids[n+1],comments[n+1])
#            n += 1
#        self.configurations.insert(0,self.analysis1)
#        self.components.insert(0,self.multiplier)
#        n = 0
#        for component in self.components :    
#            analysis_obj = Analysis.objects.get(id=ids[n])
#            self.assert_(analysis_obj.component.id == component.__class__.__name__, 'analysis component not well stored')
#            self.assert_(analysis_obj.comments == comments[n], 'analysis comments not well stored')
#            inputs = component.get_inputs()
#            for input in inputs :
#                potential_obj = analysis_obj.inputs.filter(pin__name=input.name,pin__component=analysis_obj.component)
#                self.assert_(len(potential_obj)>0, "potential of input %s not in database" % (input.name))
#                types = ['integer','float','string','date','time','datetime','pythonobject','boolean','existing']
#                for t in types :
#                    try :
#                        subclass = getattr(potential_obj[0],'potential_%s' % (t))
#                        break
#                    except :
#                        pass 
#                if t != 'existing' :  
#                    self.assert_(str(subclass.value) == str(input.potential), "potential of input %s not well stored : %s != %s" % (input.name,subclass.value,input.potential))
#                else :
#                    for t in types :
#                        try :
#                            subclass = getattr(subclass.value, 'potential_%s' % (t))
#                            break
#                        except :
#                            pass
#                    self.assert_(str(subclass.value) == str(input.potential), "existing potential of input %s not well stored : %s != %s" % (input.name,subclass.value,input.potential))
#            n += 1
#
#    def test_3_component_redefinition(self):
#        """see if components and analyses depending on a component are well destroyed when a component is re-registered""" 
#        self.multiplier.register(manager=self.manager) 
#        self.multiplier_alt.register(manager=self.manager)
#        self.multiplier.process(self.analysis1)
#        self.multiplier.snapshot(manager=self.manager) 
#        self.multiplier_alt.process(self.analysis2)
#        self.multiplier_alt.snapshot(manager=self.manager)
#        n = 0
#        for component in self.components :
#            component.register(manager=self.manager)
#            component.process(self.configurations[n], manager=self.manager)
#            component.snapshot(manager=self.manager)
#            n += 1
#        n = 0
#        for component in self.components_alt :
#            component.register(manager=self.manager)
#            component.process(self.configurations_alt[n], manager=self.manager)
#            component.snapshot(manager=self.manager)
#            n += 1
#        self.multiplier.register(manager=self.manager)
#        names = [k.__class__.__name__ for k in self.configurations_alt]
#        configurations = Analysis.objects.filter(id__in=names)
#        self.assert_(len(configurations)==len(self.configurations_alt),"some analyses not dependent from the component have been removed")
#        self.multiplier_alt.register(manager=self.manager)  
#        names = [k.__class__.__name__ for k in self.configurations]
#        configurations = Analysis.objects.filter(id__in=names)
#        self.assert_(len(configurations)==0,"some analyses dependent from the component have not been removed")    

class ComplexRegistrationTestCase(unittest.TestCase):

    def setUp(self):
        pass

    def test_1_component_registration(self):
        pass  
            
if __name__ == '__main__':
    suite = unittest.TestLoader().loadTestsFromTestCase(BaseComponentRegistrationTestCase)
    unittest.TextTestRunner(verbosity=5).run(suite)
    suite = unittest.TestLoader().loadTestsFromTestCase(ComplexComponentRegistrationTestCase)
    unittest.TextTestRunner(verbosity=5).run(suite)
