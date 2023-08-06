#encoding:utf-8
#from datetime import datetime
#from copy import copy,deepcopy
#from xml.dom.minidom import DOMImplementation
#from django.conf import settings
#from django.core.urlresolvers import reverse
#from django.utils.datastructures import SortedDict
#from django.core.paginator import Paginator
#from django.db.models.base import ModelBase
#from helmholtz.core.shortcuts import cast_object_to_leaf_class
#from helmholtz.core.modules import application_classes,get_application_classes
#from helmholtz.core.schema import get_subclasses_recursively,subclasses,get_base_class,get_parents_recursively
#from helmholtz.access_control.dependencies import get_dependencies,get_all_dependencies
#from helmholtz.core.hierarchy import node_template,get_menu_hierarchy,get_class_hierarchy,HierarchicView,constraints_template
#from helmholtz.access_control.overload import secure_delete
#from helmholtz.access_control.conditions import is_under_access_control,is_deletable_by,is_editable_by
#from helmholtz.access_control.filters import get_accessible_by
#
#class GenericWidget(object):
#    """A generic widget representing a hierarchical structure."""
#    def __init__(self,id,description,default_state='closed',user=None,width="auto"):
#        self.id = id
#        self.selection = -1
#        self.default_state = default_state
#        self.description = deepcopy(description)
#        self.extra_content = True
#        self.tables = SortedDict()
#        self.user = user
#        self.last_state = None
#        self.width = width
#        self.admin_url = reverse('admin-widget')
#    
#    def already_exists(self,dct):
#        if (dct['index'] in self.index) and (self.index[dct['index']]['title'] == dct['title']) :
#            return True
#        else :
#            return False 
#    
#    def node_is_class(self,node):
#        return (node.has_key('class') and (node['class'].__class__.__name__ == 'ModelBase'))
#    
#    def init_document(self):
#        """A html document that will receive all nodes of the widget."""
#        impl = DOMImplementation()
#        doc = impl.createDocument(None,'div',None)
#        return doc
#         
#    def init_widget(self,doc):
#        """Init id and style of the html node that will receive all nodes of the widget."""
#        widget = doc.firstChild
#        widget.setAttribute('id',self.id)
#        widget.setAttribute('class','navigator')
#        widget.setIdAttribute('id')
#        style = "width:%s%s;height:740px;overflow:auto;float:left;clear:right;" % (self.width,"px" if self.width != 'auto' else '')
#        widget.setAttribute('style',style)
#        return widget
#            
#    def display(self):
#        """Display the html representation of a hierarchical structure."""
#        #init html page
#        doc = self.init_document()
#        widget = self.init_widget(doc)
#        #organize the flat tree as a hierarchical tree
#        root_nodes = [k for k in self.nodes if (k['parent']['index'] == None)] 
#        self.visit_nodes_recursively(doc,root_nodes,widget)
#        st = widget.toprettyxml(encoding='utf-8').replace('&amp;','&').replace('&lt;','<').replace('&gt;','>') #
#        self.last_state = st
#        return st
#    
#    def get_nodes_corresponding_to_object(self,obj):
#        nodes = [k for k in self.nodes if (k['class'] == obj.__class__.__name__) and (k['id'] == obj.pk)] 
#        return nodes    
#    
#    def remove_nodes_corresponding_to_objects(self,objects):
#        for dependency in objects :
#            link_nodes = self.get_nodes_corresponding_to_object(dependency)
#            for link in link_nodes :
#                self.remove_references(link)
#    
#    def get_table_nodes(self,objects):
#        all_nodes = list()
#        for obj in objects :
#            nodes = self.get_nodes_corresponding_to_object(obj)
#            for node in nodes :
#                parent_node = self.index[node['parent']['index']]
#                if parent_node['table'] :
#                    all_nodes.append(parent_node)
#        return all_nodes
#    
#    def get_objects(self,node,manager):
#        #detect loops
#        qset = manager.all()
#        if is_under_access_control(manager.model) : 
#            qset = get_accessible_by(qset,self.user) 
#        queryset = node['node']['constraints']['queryset']
#        if queryset :
#            querydict = deepcopy(queryset['querydict'])
#            if node['object'] == 'class' :
#                dependencies = get_dependencies(node['db_object']) 
#                filter = dict()   
#                for dependency in dependencies :
#                    dct = dependencies[dependency]
#                    if (dct['class'] == manager.model) and queryset['hierarchy'] : 
#                        filter[dct['field']+'__isnull'] = True 
#                if len(filter) > 1 :
#                    raise Exception('not implemented : cannot manage multiple loops on the same class') 
#                querydict.update(filter) 
#            if querydict :
#                qset = qset.filter(**querydict)
#        order = node['node']['constraints']['order_by'] 
#        if order :   
#            fields = qset.model._meta.get_all_field_names()
#            filtered = [k for k in order if k in fields]
#            if filtered :
#                qset = qset.order_by(*filtered)
#        return qset
#    
#    def get_manager(self,node):  
#        if node['object'] == 'class' :
#            manager = node['db_object'].objects#.all()
#        elif node['object'] in ['m2m','link_list'] :
#            parent_node = self.index[node['parent']['index']]
#            if not parent_node['object'] in ['link_list_subclass','m2m_subclass'] :
#                manager = getattr(parent_node['db_object'],node['title']['original'])
#            else :
#                ancestor_node = self.index[parent_node['parent']['index']]
#                manager = getattr(ancestor_node['db_object'],parent_node['title']['original'])  
#        return manager  
#    
#    def construct_list(self,lst,parent_index,cls,node,n=0,table=None):
#        """For each object in lst, create a new node in the hierarchical structure."""
#        counter = n
#        for obj in lst :
#            node_index = "%s.%s" % (parent_index,counter)
#            dct = deepcopy(node_template)
#            dct['node'] = node['node']
#            display_base_class_only = dct['node']['constraints']['display_base_class_only']
#            dct['index'] = node_index
#            dct['class'] = obj.__class__.__name__
#            dct['id'] = obj.pk
#            dct['db_object'] = obj if not display_base_class_only else cast_object_to_leaf_class(obj)
#            dct['parent']['class'] = cls.__name__
#            dct['parent']['index'] = parent_index
#            dct['can_be_deleted'] = True
#            dct['can_be_updated'] = True
#            dct['title']['human_readable'] = obj.__unicode__()
#            dct['title']['original'] = obj.__unicode__()
#
#            if self.old_index and (dct['index'] in self.old_index) :
#                dct['state'] = self.old_index[dct['index']]['state']
#            else :
#                dct['state'] = 'closed' #if (not self.old_index) or not (dct['index'] in self.old_index) else self.old_index[dct['index']]['state']
#            
#            parent_node = self.index[parent_index]
#            if parent_node['object'] == 'class' :
#                dct['object'] = 'object'
#            else :
#                dct['object'] = 'link'
#                
#            if not self.already_exists(dct) :
#                self.nodes.append(dct)
#                self.index[node_index] = self.nodes[-1]
#                
#            force_shunt = dct['node']['constraints']['shunt']
#            if not force_shunt :
#                condition_1 = ((len(obj._meta.fields) == 1) and obj._meta.fields[0].primary_key)
#                if table :
#                    hierarchy = node['node']['objects']
#                    n_before = len(self.nodes)
#                    self._flat_tree_representation(hierarchy,obj,node_index)
#                    n_after = len(self.nodes)
#                    condition_2 = bool(n_after - n_before)
#                    dct['type'] = 'group' if (condition_2 and not condition_1) else 'leaf'
#                else :
#                    if dct['state'] != 'opened' :
#                        dp_classes = dct['node']['dependent_classes']
#                        condition_3 = bool(len([k for k in dp_classes if not (k in dct['node']['constraints']['excluded_fields']) and (dp_classes[k]['class'].__name__ in dct['node']['constraints']['links'])]))
#                    else :
#                        hierarchy = node['node']['objects']
#                        n_before = len(self.nodes)
#                        self._flat_tree_representation(hierarchy,obj,node_index)
#                        n_after = len(self.nodes)
#                        condition_3 = bool(n_after - n_before)
#                    dct['type'] = 'group' if (not condition_1) or condition_3 else 'leaf'
#            else :
#                dct['state'] = 'closed'
#                dct['type'] = 'leaf'
#            
#            counter += 1
#            
#    def expand_class_node(self,node,table=None):
#        parent_index = node['index']
#        manager = self.get_manager(node)
#        qset = self.get_objects(node,manager)
#        if not table :
#            self.construct_list(qset,parent_index,manager.model,node)
#        else :
#            #create a new paginator each time the node is opened
#            #to ensure that paginated list is synchronized with the object list
#            #but the page must be memorized from expansion to another
#            self.reset_paginator(node,parent_index,table,qset)    
#            lst = self.tables[parent_index]['paginator'].page(self.tables[parent_index]['page']).object_list
#            self.construct_list(lst,parent_index,manager.model,node,0,table)
#    
#    def expand_object_node(self,node):
#        hierarchy = node['node']['objects']
#        cls = node['node']['class']
#        obj = cls.objects.get(pk=node['id'])
#        self._flat_tree_representation(hierarchy,obj,node['index']) 
#    
#    def expand_link_node(self,node,table,default_order_by=None,default_ordering=None,default_page=None):
#        if table : 
#            if not self.tables.has_key(node['index']) :
#                self.tables[node['index']] = dict()
#                self.reset_table_parameters(node,table,default_order_by,default_ordering,default_page)
#
#    def expand_tree(self,node):
#        if node['object'] == 'class' : 
#            if not node['table'] :
#                self.expand_class_node(node)
#            else :
#                self.expand_class_node(node,node['table'])
#        elif node['object'] == 'object' :
#            self.expand_object_node(node)
##        elif node['object'] == 'fkey' :
##            self.expand_fkey_node(node)
#        elif node['object'] in ['link_list','m2m'] :
#            if node['table'] :
#                self.expand_link_node(node,node['table'])
#            else :
#                pass
#        else :
#            pass
#        
#    def open(self,index):
#        node = self.index[index]
#        node['state'] = 'opened'
#        self.expand_tree(node)
#            
#    def close(self,index):
#        node = self.index[index]
#        node['state'] = 'closed'
#        #self.collapse_tree(node)
#    
#    def map_old_state(self,node,old_nodes,new_nodes,tables=None,preselect=False):
#        for child in old_nodes :
#            selected = None
#            old_node_splitted_index = child['index'].split('.')
#            old_node_relative_index = int(old_node_splitted_index[-1])
#            for new_node in new_nodes :
#                new_node_splitted_index = new_node['index'].split('.')
#                new_node_relative_index = int(new_node_splitted_index[-1])
#                if (len(old_node_splitted_index) == len(new_node_splitted_index)) and ((old_node_splitted_index[0:-1] == new_node_splitted_index[0:-1]) or preselect) and (new_node_relative_index == old_node_relative_index) :
#                    selected = new_node
#            if selected :
#                selection = self.index[selected['index']]
#                self.index[selected['index']]['state'] = child['state'] if ((selection['type'] != 'leaf') and (selection['object'] != 'subclass_header')) else 'closed'  
#                if (selection['state'] == 'opened') and self.index[selection['index']]['table']  :
#                    if tables :
#                        if tables.has_key(selection['index']) :
#                            to_refresh = tables[selection['index']]
#                            self.reset_table_parameters(selection,selection['table'],default_order_by=to_refresh['order_by'],default_ordering=to_refresh['ordering'],default_page=to_refresh['page'])    
#                    else :
#                        self.reset_table_parameters(selection,selection['table']) 
#
#    def refresh_all(self,node):
#        self.old_tables = deepcopy(self.tables)
#        self.old_index = deepcopy(self.index)
#        nodes = [k for k in self.nodes if (k['object'] == 'class') and ((len(k['can_create'])<2) or (k['parent']['class'] == k['class']))]
#        for node in nodes :
#            old_nodes = self.get_children(node,recursive=True)
##            old_tables = SortedDict()
##            for child in old_nodes :
##                if child['index'] in self.tables :
##                    old_tables[child['index']] = self.tables[child['index']]
#            self.remove_nodes(old_nodes)
#            self.expand_class_node(node,node['table'])
#            children = self.get_children(node,recursive=False)
#            if len(children):   
#                node['type'] = 'group'
#            else :
#                node['type'] = 'leaf'
#                node['state'] = 'closed'
##            new_nodes = self.get_children(node,recursive=True)
##            self.map_old_state(node,old_nodes,new_nodes,old_tables)
#        self.old_tables = None
#        self.old_index = None
#    
#    def delete_selected_only(self,obj,selected_objects,fields=None,starting_point=True):
#        if starting_point and not fields :
#            fields = get_dependencies(obj.__class__)
#        for field in fields :
#            attr = getattr(obj,field)
#            if attr.__class__.__name__ == 'RelatedManager' :
#                new_fields = get_dependencies(attr.model)
#                objects = attr.all()
#                for sub_obj in objects : 
#                    #unlink sub objects if they are not selected
#                    object_field = getattr(sub_obj.__class__,fields[field]['field'])
#                    not_required = object_field.field.null
#                    if not (sub_obj in selected_objects) and not_required : 
#                        attr.clear()
#                        setattr(sub_obj,fields[field]['field'],None)
#                    if new_fields :
#                        self.delete_selected_only(sub_obj,selected_objects,new_fields,False)          
#            else :
#                if not (attr in selected_objects) : 
#                    setattr(obj,field,None)
#                new_fields = get_dependencies(attr.__class__)
#                if new_fields :
#                    self.delete_selected_only(attr,selected_objects,new_fields,False)   
#        #finally remove main object and those in selected_objects  
#        if starting_point :
#            for selected in selected_objects :
#                selected.delete()
#            obj.delete()
#
#    def get_selected_objects(self,selection):
#        classes = [k for k in application_classes]
#        names = [k.__name__ for k in classes]
#        selected_objects = [k.split('.') for k in selection]
#        selected_objects = [classes[names.index(k[0])].objects.get(pk=k[1]) for k in selected_objects]
#        return selected_objects
#    
#    def new_node_dct(self,node,instance):
#        dct = deepcopy(node_template)
#        dct['class'] = node['class']
#        dct['id'] = instance.pk
#        dct['db_object'] = instance
#        dct['parent']['index'] = str(node['index'])
#        dct['title']['human_readable'] = instance.__unicode__()
#        dct['title']['original'] = instance.__unicode__()
#        dct['type'] = 'group' 
#        dct['state'] = 'closed'
#        if node['node'] :
#            dct['node'] = node['node']
#        else :
#            references = [k for k in self.nodes if (k['class'] == node['class']) and (k['object'] == 'class')]
#            assert references, "constraints of class %s not defined" % (node['class'])
#            dct['node'] = references[0]['node']
#        dct['object'] = 'object' if (node['object'] == 'class') else 'link'
#        return dct
#
#    def delete_object(self,node,delete_all,selection):
#        obj = node['db_object']
#        all_table_nodes = self.get_table_nodes([obj])
#        #self.remove_references(node)
#        #parent_node = self.index[node['parent']['index']]
#        fields = node['node']['dependent_classes']
#        if not delete_all :
#            selected_objects = self.get_selected_objects(selection)
#            table_nodes = self.get_table_nodes(selected_objects)
#            all_table_nodes.extend(table_nodes)
#            #self.remove_nodes_corresponding_to_objects(selected_objects)
#            secure_delete(obj,self.user,selected_objects,filter=True)
##            if is_under_access_control() : 
##                secure_delete(obj,self.user,selected_objects,filter=True)
##            else :
##                self.delete_selected_only(obj,selected_objects,fields)
#        else :
#            selected_objects = [k[1] for k in get_all_dependencies(obj,fields,self.user)]
#            table_nodes = self.get_table_nodes(selected_objects)
#            all_table_nodes.extend(table_nodes)
#            #self.remove_nodes_corresponding_to_objects(selected_objects)
#            secure_delete(obj,self.user,selected_objects,filter=True)
#        #update tables after deletion because of paginator refresh
##        for parent_node in all_table_nodes :
##            self.reset_table_for_delete(parent_node)
#        #raise Exception('test')
#        #selected_objects.insert(0,node)
#        #widget.remove_nodes_corresponding_to_objects(selected_objects)
#    
#    def remove_nodes(self,nodes):
#        for node in nodes :
#            i = node['index']
#            k = self.nodes.index(node)
#            if self.index.has_key(i) :
#                self.index.pop(i)
#            if self.tables.has_key(i) :
#                self.tables.pop(i)
#            self.nodes.pop(k)
#    
#    def get_children(self,node,children=None,recursive=False,starting_point=True):
#        if starting_point :
#            children = list()
#            self.nodes.sort(key=self.index_weight)
#         
#        new_children = [k for k in self.nodes if (k['parent']['index'] == node['index'])]
#        for child in new_children :
#            if not (child in children) :
#                children.append(child)
#                if recursive : 
#                    self.get_children(child,children,recursive,False)
#        if starting_point :
#            return children
#    
#    def retrieve_property_value(self,obj,node_id,properties,property_name):   
#        try : 
#            attr = getattr(obj,property_name) 
#            if (attr.__class__.__class__.__name__ == 'ModelBase') or (attr.__class__.__name__ in ['ImageFieldFile','FieldFile','PhysicalQuantity']) :
#                return attr.__unicode__()
#            else :
#                return attr 
#        except :           
#            property = [k[0] for k in properties if (k[1] == property_name)]
#            assert property, 'property %s not specified in constraints' % (property_name)
#            splitted_property = property[0].split('.')
#            if len(splitted_property) < 2 :
#                try :
#                    obj_attr = getattr(obj,property[0])
#                except :
#                    obj_attr = None 
#            else :
#                try :
#                    obj_attr = getattr(obj,splitted_property[0])
#                    for property in splitted_property[1:] :
#                        if callable(obj_attr) :
#                            obj_attr = obj_attr()
#                        if not (obj_attr is None) : 
#                            try : 
#                                obj_attr = getattr(obj_attr,property)
#                            except :
#                                obj_attr = None
#                        else :
#                            break
#                except :
#                    obj_attr = None
#            if callable(obj_attr) :
#                value = obj_attr()
#            else :
#                value = obj_attr
#            return unicode(value)
#    
#    def reorder_table(self,node_id,order_by,ordering):
#        #refresh 
#        self.tables[node_id]['order_by'] = order_by
#        self.tables[node_id]['ordering'] = ordering
#        node = self.index[node_id]
#        if node['object'] in ['class','link_list','m2m'] :
#            nodes = self.get_children(node,recursive=True)
#            for child in nodes :
#                #child = self.index[item['index']]
#                self.nodes.pop(self.nodes.index(child))
#                self.index.pop(child['index'])
#            self.expand_class_node(node,node['table'])
#        else :
#            raise Exception('not implented case')
##            self.tables[node_id]['paginator'].object_list.sort(key=lambda x:self.retrieve_property_value(x,node_id,node['node']['constraints']['properties'],self.tables[node_id]['order_by']))
##            if self.tables[node_id]['ordering'] == 'descending' :
##                self.tables[node_id]['paginator'].object_list.reverse()
#    
#    def define_order(self,structure,table,default_order_by=None,default_ordering=None):
#        if default_order_by :
#            order_by = default_order_by
#        elif structure['constraints']['order_by'] :
#            order_by = structure['constraints']['order_by'][0]
##            elif cls._meta.ordering :
##                order_by = cls._meta.ordering[0]
##                is_descending = order_by.startswith('-') 
##                tables[forced_index]['order_by'] = order_by if not is_descending else order_by[1:]
##                tables[forced_index]['ordering'] = 'descending' if is_descending else 'ascending'
#        elif table['fields'] :
#            order_by = table['fields'][0] 
#        else :
#            order_by = structure['objects'].hierarchy['fields'][0] 
#        if default_ordering :
#            ordering = default_ordering
#        else :
#            ordering = structure['constraints']['ordering'] if structure['constraints']['ordering'] else 'ascending'
#        return order_by,ordering
#    
#    def reset_table_parameters(self,node,table,lst=None,default_order_by=None,default_ordering=None,default_page=None):
#        structure = node['node']
#        table = node['node']['constraints']['table']
#        self.tables[node['index']]['order_by'],self.tables[node['index']]['ordering'] = self.define_order(structure,table,default_order_by=default_order_by,default_ordering=default_ordering)
#        objects = [k['db_object'] for k in self.nodes if (k['parent']['index'] == node['index'])] if not lst else lst
#        self.tables[node['index']]['paginator'] = Paginator(objects,table['pagination'])
#        self.tables[node['index']]['paginator'].object_list.sort(key=lambda x:self.retrieve_property_value(x,node['index'],node['node']['constraints']['properties'],self.tables[node['index']]['order_by']))
#        if self.tables[node['index']]['ordering'] == 'descending' :
#            self.tables[node['index']]['paginator'].object_list.reverse()
#        if default_page :
#            if default_page > self.tables[node['index']]['paginator'].num_pages :
#                self.tables[node['index']]['page'] = self.tables[node['index']]['paginator'].num_pages
#            else :
#                self.tables[node['index']]['page'] = default_page
#        else :
#            self.tables[node['index']]['page'] = 1
#        self.tables[node['index']]['paginator'].page(self.tables[node['index']]['page'])
#    
#    def reset_paginator(self,node,parent_index,table,qset):
#        index = node['parent']['index']
#        parent_node = self.index[index] if index else self.index[node['index']]
#        #necessary to reorder in case of subclass
#        if not parent_node['object'] in ['link_list_subclass','m2m_subclass'] :
#            lst = list(qset)  
#        else :
#            pks = [k.pk for k in qset]
#            cls = node['node']['class']
#            manager = cls.objects
#            objects = manager.filter(pk__in=pks)
#            if is_under_access_control(manager.model) :
#                objects = get_accessible_by(objects,self.user)
#            lst = list(objects)
#        if not self.old_tables or not node['index'] in self.old_tables :
#            #self.reset_table_parameters(node,table,lst=lst)
#            self.tables[parent_index]['paginator'] = Paginator(lst,table['pagination'])
#            self.tables[parent_index]['paginator'].object_list.sort(key=lambda x:self.retrieve_property_value(x,node['index'],node['node']['constraints']['properties'],self.tables[parent_index]['order_by']))
#            if self.tables[parent_index]['ordering'] == 'descending' :
#                self.tables[parent_index]['paginator'].object_list.reverse()
#        elif node['index'] in self.old_tables :
#            old_table = self.old_tables[node['index']]
#            self.reset_table_parameters(node,table,lst=lst,default_order_by=old_table['order_by'],default_ordering=old_table['ordering'],default_page=old_table['page'])
#    
#    def select_page(self,node_id,page):
#        node = self.index[node_id]
#        old_page = self.tables[node_id]['page']
#        self.tables[node_id]['page'] = page
#        self.tables[node_id]['paginator'].page(page)
#        #reset the table to put data of another page
#        #not performed for link_list and link_list_subclass nodes
#        if not (node['object'] in ['link_list_subclass','m2m_subclass']) :
#            children = self.get_children(node,recursive=True)
#            old_tables = SortedDict()
#            for child in children :
#                if child['index'] in self.tables :
#                    old_tables[child['index']] = self.tables[child['index']] 
#            old_root_children = self.get_children(node,recursive=False)
#            old_root_and_children = list()
#            for old_root_child in old_root_children :
#                old_root_and_children.append((old_root_child,self.get_children(old_root_child,recursive=True)))
#            tmp = [k[1] for k in old_root_and_children]
#            for lst in tmp :
#                self.remove_nodes(lst)
#            self.remove_nodes(old_root_children)
#            
#            #old_children = self.get_children(node,recursive=True)
#            #self.remove_nodes(old_children)
#            self.expand_class_node(node,node['table'])
#
#            if old_page == page :
#                new_root_children = self.get_children(node,recursive=False)
#                new_root_and_children = list()
#                for new_root_child in new_root_children :
#                    new_root_and_children.append((new_root_child,self.get_children(new_root_child,recursive=True)))
#                to_open = [k for k in old_root_children if k['state'] == 'opened'] 
#                
#                for old_item in to_open :
#                    new_item = None
#                    for new_root_child in new_root_children :
#                        if (new_root_child['class'] == old_item['class']) and (new_root_child['id'] == old_item['id']) :
#                            new_item = new_root_child
#                            break
#                    
#                    if new_item :
#                        self.open(new_item['index'])
#                        old_nodes = [k[1] for k in old_root_and_children if k[0]['index'] == old_item['index']]
#                        new_nodes = [k[1] for k in new_root_and_children if k[0]['index'] == new_item['index']]
#                        if old_nodes and new_nodes :
#                            old_children = old_nodes[0]
#                            new_children = new_nodes[0]
#                            #self.map_old_state(new_item,old_children,new_children,tables=old_tables,preselect=True)
# 
##                to_open = [k for k in old_children if k['state'] == 'opened']
##                for item in to_open :
##                    self.open(item['index'])
##                new_children = self.get_children(node,recursive=True)
##                self.map_old_state(node,old_children,new_children)     
#        else :
#            pass
#    
#    def create_button(self,widget,action,href,identifier,enabled=True):
#        action_node = widget.createElement('span')
#        action_node.setAttribute('id','%s_button_%s'%(action,identifier))
#        action_node.setIdAttribute('id')
#        link_node = widget.createElement('a')
#        if enabled :
#            action_node.setAttribute('class','%s_button'% (action))
#            link_node.setAttribute('href',href)
#        else :
#            action_node.setAttribute('class','%s_button_gr'% (action))
#        link_node.setAttribute('class','button')
#        content_node = widget.createElement('span')
#        content_node.setAttribute('class','invisible_content')
#        content_text = widget.createTextNode('invisible_content')
#        content_node.appendChild(content_text)
#        link_node.appendChild(content_node)
#        action_node.appendChild(link_node)
#        return action_node
#    
#    def make_header(self,node,widget,node_type,selection_state,identifier):
#        #header
#        header_class = "%s_header_%s_and_%s" % (node_type,node['state'],selection_state)
#        header_node = widget.createElement('div')
#        header_node.setAttribute('id','header_%s' % (identifier))
#        header_node.setIdAttribute('id')
#        header_node.setAttribute('class',header_class)
#        return header_node
#    
#    def make_title(self,node,widget,node_type,selection_state,identifier):
#        #title
#        title_node = widget.createElement('span')
#        title_node.setAttribute('id','title_%s' % (identifier))
#        title_node.setIdAttribute('id')
#        title_node.setAttribute('class','%s_title_%s'%(node_type,selection_state))
#        hrtitle = node['title']['human_readable']
#        if not (node['value'] is None) and (node['object'] in ['link','fkey','value','property']) :
#            title_span = widget.createElement('span')
#            if (node['object'] in  ['fkey','link']) and ((len(node['can_create'])>1) or (node['type'] == 'group')) and (node['value'] != 'N.D') :
#                text_node = widget.createTextNode("%s" % hrtitle)
#                title_span.appendChild(text_node)
#                content_span = widget.createElement('span')
#                title_node.appendChild(title_span)
#            else :
#                text_node = widget.createTextNode("%s : " % hrtitle)
#                title_span.appendChild(text_node)
#                content_span = widget.createElement('span')
#                title_node.appendChild(title_span)
#                if not (node['class'] in ['ImageFieldFile','FieldFile']) or (node['value'] == 'N.D') :
#                    content_span.setAttribute('class','node_field_value') 
#                    text_node = widget.createTextNode("%s" % (node['value'] if node['value'] else 'N.D'))
#                    content_span.appendChild(text_node)
#                    title_node.appendChild(content_span)
#                else :
#                    if node['class'] == 'ImageFieldFile' :
#                        image_node = widget.createElement('img')
#                        src = "/media/%s" % (node['value'])
#                        image_node.setAttribute('src',src)
#                        title_span.setAttribute('class','title_before_image')
#                        image_span = widget.createElement('span')
#                        image_span.setAttribute('class','image_node')
#                        image_span.appendChild(image_node)
#                        title_node.appendChild(image_span)
#                    elif node['class'] == 'FieldFile' :
#                        raise Exception('not implemented case')
#        else :
#            title = hrtitle
#            if (node['value'].__class__.__class__.__name__ == 'ModelBase') :
#                title = '%s : %s' %(title,node['value'])    
#            text_node = widget.createTextNode(title)
#            title_node.appendChild(text_node)
#        return title_node
#    
#    def make_expander(self,node,widget,node_type,action,identifier):
#        #expander of header
#        expander_node = widget.createElement('span')
#        expander_node.setAttribute('id','expander_%s' % (identifier))
#        expander_node.setIdAttribute('id')
#        if node['type'] != 'group' :
#            expander_class = "%s_disabled_expander" % (node_type)
#            dot_node = widget.createElement('div')
#            dot_node.setAttribute('class','dot')
#            content_node = widget.createElement('div')
#            content_node.setAttribute('class','invisible_content')
#            content_text = widget.createTextNode('invisible_content')
#            content_node.appendChild(content_text)
#            dot_node.appendChild(content_node)
#            expander_node.appendChild(dot_node)
#        else :
#            expander_class = "%s_expander_%s" % (node_type,node['state'])
#            link_node = widget.createElement('a')
#            link_node.setAttribute('href',self.admin_url + '?action=%s&widget_id=%s&node_id=%s'%(action,self.id,node['index']))
#            link_node.setAttribute('class','button')
#            content_node = widget.createElement('div')
#            content_node.setAttribute('class','invisible_content')
#            content_text = widget.createTextNode('invisible_content')
#            content_node.appendChild(content_text)
#            link_node.appendChild(content_node)
#            expander_node.appendChild(link_node)
#        expander_node.setAttribute('class',expander_class)
#        return expander_node
#    
#    def define_actions(self,node,widget,header_node,identifier):
#        #define actions relative to a node
#        list_of_actions = None
#        if node['object'] != 'module' :
#            parent_index = node['parent']['index']
#            parent_node = self.index[parent_index] if parent_index else self.index[node['index']]
#            db_object = node['db_object']
#            access_control = (db_object.__class__.__class__ == ModelBase) and is_under_access_control(db_object)
#            can_delete = not access_control or is_deletable_by(db_object,self.user)  
#            can_modify = not access_control or is_editable_by(db_object,self.user)
#            if (node['object'] == 'class') :
#                list_of_actions = node['node']['constraints']['actions'] if node['node'] else None
#                action = 'add_object'
#                if not list_of_actions or (action in list_of_actions) :
#                    href = self.admin_url + '?action=%s&widget_id=%s&node_id=%s'%(action,self.id,node['index'])
#                    action_node = self.create_button(widget,action,href,identifier)
#                    header_node.appendChild(action_node)  
#            elif (node['object'] in ['m2m','link_list']) :
#                #display_contenttype_form_before = (node['db_object'].__name__=='GenericMeasurement')
#                display_parameter_form_before = (node['db_object'].__name__=='GenericMeasurement')
#                #display_class_form_before = int(not display_contenttype_form_before and len(node['can_create']) > 1 and node['node']['constraints']['display_base_class_only'])
#                display_class_form_before = int(not display_parameter_form_before and len(node['can_create']) > 1 and node['node']['constraints']['display_base_class_only'])
#                #display_contenttype_form_before = int(display_contenttype_form_before)
#                display_parameter_form_before = int(display_parameter_form_before)
#                list_of_actions = node['node']['constraints']['actions'] if node['node'] else None
#                action = 'add_object'
#                #limit the number of object in the list
#                limit_number_of_objects = False
#                if node['table'].has_key('length') and node['table']['length'] :
#                    sub_nodes = self.get_children(node,recursive=False)
#                    if len(sub_nodes) >= node['table']['length'] :
#                        limit_number_of_objects = True 
#                if (node['object'] == 'm2m') or (parent_node['object'] == 'm2m_subclass') :
#                    is_required = False
#                else :
#                    dependent_classes = parent_node['node']['dependent_classes']
#                    found = False
#                    for cls in dependent_classes :
#                        if dependent_classes[cls]['class'] == node['db_object'] :
#                            found = True
#                            break    
#                    is_required = dependent_classes[cls]['is_required'] if found else False  
#                if (not list_of_actions or (action in list_of_actions)) and not limit_number_of_objects :
##                    href = self.admin_url + '?action=%s&widget_id=%s&node_id=%s&display_class_form_before=%s&display_contenttype_form_before=%s'%(action,self.id,node['index'],display_class_form_before,display_contenttype_form_before)
#                    href = self.admin_url + '?action=%s&widget_id=%s&node_id=%s&display_class_form_before=%s&display_parameter_form_before=%s'%(action,self.id,node['index'],display_class_form_before,display_parameter_form_before)
#                    action_node = self.create_button(widget,action,href,identifier,can_modify)
#                    header_node.appendChild(action_node) 
#                action = 'link_object'
#                if not is_required and (not list_of_actions or (action in list_of_actions)) and not limit_number_of_objects :
##                    href = self.admin_url + '?action=%s&widget_id=%s&node_id=%s&display_class_form_before=%s&display_contenttype_form_before=%s'%(action,self.id,node['index'],display_class_form_before,display_contenttype_form_before)
#                    href = self.admin_url + '?action=%s&widget_id=%s&node_id=%s&display_class_form_before=%s&display_parameter_form_before=%s'%(action,self.id,node['index'],display_class_form_before,display_parameter_form_before)
#                    action_node = self.create_button(widget,action,href,identifier,can_modify)
#                    header_node.appendChild(action_node)      
#            elif (node['object'] == 'object') :
#                parent_object = parent_node['db_object']
#                cls = parent_object.__class__ if (parent_object.__class__.__name__ != 'ModelBase') else parent_object
#                parent_access_control = is_under_access_control(cls)
#                can_modify_parent = not parent_access_control or is_editable_by(parent_object,self.user)
#                list_of_actions = parent_node['node']['constraints']['actions'] if parent_node['node'] else None
#                action = 'delete_object'
#                if not list_of_actions or (action in list_of_actions) :
#                    href = self.admin_url + '?action=%s&widget_id=%s&node_id=%s'%(action,self.id,node['index'])#,node['class'],node['id'])
#                    action_node = self.create_button(widget,action,href,identifier,can_delete)
#                    header_node.appendChild(action_node)
#                if parent_node['object'] != 'class' : 
#                    action = 'unlink_object'
#                    if not list_of_actions or (action in list_of_actions) :
#                        href = self.admin_url + '?action=%s&widget_id=%s&node_id=%s'%(action,self.id,node['index'])
#                        action_node = self.create_button(widget,action,href,identifier,can_modify or can_modify_parent)
#                        header_node.appendChild(action_node)
#                action = 'modify_object'
#                if not list_of_actions or (action in list_of_actions) :
#                    href = self.admin_url + '?action=%s&widget_id=%s&node_id=%s'%(action,self.id,node['index'])
#                    action_node = self.create_button(widget,action,href,identifier,can_modify)
#                    header_node.appendChild(action_node)     
#            elif (node['object'] == 'link') and ((node['type'] == 'group') or (node['value'] != 'N.D')) :
#                if parent_node['object'] == 'm2m' :
#                    is_required = False
#                elif (parent_node['object'] == 'link_list') :
#                    ancestor_node = self.index[parent_node['parent']['index']]
#                    if not ancestor_node['object'] in ['link_list_subclass','m2m_subclass'] :
#                        field = ancestor_node['node']['dependent_classes'][parent_node['title']['original']]
#                        is_required = field['is_required']
#                    else :
#                        parent_ancestor = self.index[ancestor_node['parent']['index']]
#                        if ancestor_node['object'] == 'm2m_subclass' :
#                            is_required = False
#                        else :
#                            field = parent_ancestor['node']['dependent_classes'][ancestor_node['title']['original']]
#                            is_required = field['is_required']
#                elif (parent_node['object'] != 'link_list') :
#                    field = parent_node['node']['dependent_classes'][node['title']['original']]
#                    is_required = field['is_required']
#
#                parent_object = parent_node['db_object']
#                cls = parent_object.__class__ if (parent_object.__class__.__name__ != 'ModelBase') else parent_object
#                parent_access_control = is_under_access_control(cls)
#                can_modify_parent = not parent_access_control or is_editable_by(node['db_object'],self.user)
#                list_of_actions = parent_node['node']['constraints']['actions'] if parent_node['node'] else None
#                action = 'delete_object'
#                if not list_of_actions or (action in list_of_actions) :
#                    href = self.admin_url + '?action=%s&widget_id=%s&node_id=%s'%(action,self.id,node['index'])
#                    action_node = self.create_button(widget,action,href,identifier,can_delete)
#                    header_node.appendChild(action_node)
#                action = 'unlink_object'
#                if not is_required and (not list_of_actions or (action in list_of_actions)) :
#                    href = self.admin_url + '?action=%s&widget_id=%s&node_id=%s'%(action,self.id,node['index'])
#                    action_node = self.create_button(widget,action,href,identifier,can_modify or can_modify_parent)
#                    header_node.appendChild(action_node)
#                action = 'modify_object'
#                if not list_of_actions or (action in list_of_actions) :
#                    href = self.admin_url + '?action=%s&widget_id=%s&node_id=%s'%(action,self.id,node['index'])
#                    action_node = self.create_button(widget,action,href,identifier,can_modify)
#                    header_node.appendChild(action_node)
#            elif (node['object'] == 'link') and ((node['type'] == 'leaf') and not node['value'] != 'N.D') :
#                list_of_actions = node['node']['constraints']['actions'] if node['node'] else None
#                display_class_form_before = int(len(node['can_create']) > 1)
#                action = 'add_object'
#                if not list_of_actions or (action in list_of_actions) :
#                    href = self.admin_url + '?action=%s&widget_id=%s&node_id=%s&display_class_form_before=%s'%(action,self.id,node['index'],display_class_form_before)
#                    action_node = self.create_button(widget,action,href,identifier)
#                    header_node.appendChild(action_node) 
#                action = 'link_object'
#                if not list_of_actions or (action in list_of_actions) :
#                    href = self.admin_url + '?action=%s&widget_id=%s&node_id=%s&display_class_form_before=%s'%(action,self.id,node['index'],display_class_form_before)
#                    action_node = self.create_button(widget,action,href,identifier)
#                    header_node.appendChild(action_node)
#            elif (node['object'] == 'fkey') and (node['value'] != 'N.D') :
#                parent_object = parent_node['db_object']
#                if (parent_node['object'] != 'subclass_header') :
#                    dependent_classes = node['node']['dependent_classes']
#                    found = False
#                    for cls in dependent_classes :
#                        if dependent_classes[cls]['field'] == node['title']['original'] :
#                            found = True
#                            break    
#                    is_required = dependent_classes[cls]['is_required'] if found else False
#                else :
#                    dependent_classes = node['node']['dependent_classes']
#                    base = get_base_class(parent_node['db_object'].__class__)
#                    found = False
#                    for cls in dependent_classes :
#                        if dependent_classes[cls]['class'] == base :
#                            found = True
#                            break
#                    is_required = dependent_classes[cls]['is_required'] if found else False    
#                parent_access_control = is_under_access_control(parent_object.__class__)
#                can_modify_parent = not parent_access_control or is_editable_by(parent_object,self.user)
#                list_of_actions = node['node']['constraints']['actions'] if node['node'] else None
#                action = 'delete_object'
#                if not list_of_actions or (action in list_of_actions) :
#                    href = self.admin_url + '?action=%s&widget_id=%s&node_id=%s'%(action,self.id,node['index'])
#                    action_node = self.create_button(widget,action,href,identifier,can_delete)
#                    header_node.appendChild(action_node)
#                action = 'unlink_object'
#                if not is_required and (not list_of_actions or (action in list_of_actions)) :
#                    href = self.admin_url + '?action=%s&widget_id=%s&node_id=%s'%(action,self.id,node['index'])
#                    action_node = self.create_button(widget,action,href,identifier,can_modify_parent)
#                    header_node.appendChild(action_node)
#                action = 'modify_object'
#                if not list_of_actions or (action in list_of_actions) :
#                    href = self.admin_url + '?action=%s&widget_id=%s&node_id=%s'%(action,self.id,node['index'])
#                    action_node = self.create_button(widget,action,href,identifier,can_modify)
#                    header_node.appendChild(action_node)
#            elif (node['object'] == 'fkey') and (node['value'] == 'N.D') :
#                parent_object = parent_node['db_object']
#                parent_access_control = is_under_access_control(parent_object.__class__)
#                can_modify_parent = not parent_access_control or is_editable_by(parent_object,self.user)
#                list_of_actions = node['node']['constraints']['actions'] if node['node'] else None
#                display_class_form_before = int(len(node['can_create']) > 1)
#                action = 'add_object'
#                if not list_of_actions or (action in list_of_actions) :
#                    href = self.admin_url + '?action=%s&widget_id=%s&node_id=%s&display_class_form_before=%s'%(action,self.id,node['index'],display_class_form_before)
#                    action_node = self.create_button(widget,action,href,identifier,can_modify_parent)
#                    header_node.appendChild(action_node) 
#                action = 'link_object'
#                if not list_of_actions or (action in list_of_actions) :
#                    href = self.admin_url + '?action=%s&widget_id=%s&node_id=%s&display_class_form_before=%s'%(action,self.id,node['index'],display_class_form_before)
#                    action_node = self.create_button(widget,action,href,identifier,can_modify_parent)
#                    header_node.appendChild(action_node)
#            elif (node['object'] == 'link') and (node['type'] == 'leaf') :
#                list_of_actions = node['node']['constraints']['actions'] if node['node'] else None
#                action = 'add_object'
#                if not list_of_actions or (action in list_of_actions) :
#                    href = self.admin_url + '?action=%s&widget_id=%s&node_id=%s'%(action,self.id,node['index'])
#                    action_node = self.create_button(widget,action,href,identifier)
#                    header_node.appendChild(action_node)  
##                action = 'link_object'
##                href = self.admin_url + '?action=%s&widget_id=%s&node_id=%s'%(action,self.id,node['index'])
##                action_node = self.create_button(widget,action,href,identifier)
##                header_node.appendChild(action_node)
#        return list_of_actions
#    
#    def init_node(self,node):
#        identifier = "%s_%s" % (self.id,node['index'])
#        if node['parent']['index'] != None :
#            node_type = 'node'    
#        else :
#            node_type = 'root_node'    
#        if node['index'] == self.selection :
#            selection_state = 'selected'
#        else :
#            selection_state = 'not_selected'
#        if node['state'] == 'closed' :
#            action = 'open'
#        elif node['state'] == 'opened' :
#            action = 'close'
#        return identifier,node_type,action,selection_state
#    
#    def init_domnode(self,widget,identifier):
#        docnode = widget.createElement('div')
#        docnode.setAttribute('id',identifier)
#        docnode.setIdAttribute('id')   
#        return docnode
#    
#    def make_container(self,node,widget,node_type,identifier):
#        #container
#        container_class = "%s_container_%s" % (node_type,node['state'])
#        container_node = widget.createElement('div')
#        container_node.setAttribute('id','container_%s' % (identifier))
#        container_node.setIdAttribute('id') 
#        return container_node,container_class
#    
#    def append_header_and_container(self,docnode,header_node,container_node):
#        #append header and container to node
#        docnode.appendChild(header_node)
#        docnode.appendChild(container_node)
#    
#    def get_table_fields(self,node,hierarchy,expansion):
#        #get the full list of attributes to display in the table header
#        #if fields are not specified in constraints
#        #the expansion parameter prevents adding fields into the header
#        if not node['table']['fields'] :
#            table_fields = list()
#            value_types = ['fields','properties']
#            object_types = ['foreign_keys','reverse_one_to_one_keys','generic_foreign_keys']
#            field_types = copy(value_types)
#            field_types.extend(object_types)
#            for field_type in field_types :
#                if hierarchy.has_key(field_type) :
#                    for field in hierarchy[field_type] :
#                        if not field in expansion :
#                            if field_type != 'properties' :
#                                table_fields.append(field)
#                            else :
#                                table_fields.append(field[1])
#        else :
#            table_fields = node['table']['fields']
#        return table_fields
#    
#    def prepare_table(self,node):
#        hierarchy = node['node']['objects'].hierarchy
#        expansion = copy(node['table']['expansion'])
#        in_expander = [k for k in expansion if not k.startswith('-')]
#        out_expander = [k[1:] for k in expansion if k.startswith('-')]
#        #by default foreign_keys are stored in the expander in order to edit sub-objects
#        #reverse links are stored if classes are specified in constraint links
#        for field_type in ['foreign_keys','reverse_one_to_one_keys','reverse_foreign_keys','reverse_many_to_many_fields','many_to_many_fields','generic_relations','generic_foreign_keys'] :
#            if hierarchy.has_key(field_type) :
#                for field in hierarchy[field_type] :
#                    if not (field in in_expander) and not (field in out_expander) :
#                        in_expander.append(field)
#        return hierarchy,expansion,in_expander,out_expander
#    
#    def make_table_node(self,node,widget,identifier):
#        table_node = widget.createElement('table')
#        table_node.setAttribute('id','table_%s' % (identifier))
#        if not node['table']['width'] is None :
#            table_node.setAttribute('width',"%spx" % (node['table']['width']))
#        table_node.setIdAttribute('id')
#        table_node.setAttribute('cellspacing','0')
#        return table_node
#    
#    def append_field_labels(self,node,widget,table_fields,row_node):
#        #add fields label into the table header
#        for value in table_fields :
#            if value in node['db_object']._meta.get_all_field_names() :
#                hr_field = node['db_object']._meta.get_field_by_name(value)
#                if hr_field[2] or (hr_field[0].__class__.__name__ != 'RelatedObject'):
#                    hr_field = hr_field[0].verbose_name.lower()
#                else :
#                    hr_field = value
#            else :
#                hr_field = value 
#            column_node = widget.createElement('th')
#            order_link = widget.createElement('a')
#            if value != self.tables[node['index']]['order_by'] :
#                ordering = 'ascending'
#            elif self.tables[node['index']]['ordering'] == 'ascending' :
#                ordering = 'descending' 
#            elif self.tables[node['index']]['ordering'] == 'descending' :
#                ordering = 'ascending' 
#            order_link.setAttribute('href',self.admin_url + '?action=%s&widget_id=%s&node_id=%s&order_by=%s&ordering=%s'%('sort_table',self.id,node['index'],value,ordering))
#            order_link.setAttribute('class','ordering_field')
#            text_node = widget.createTextNode(hr_field)
#            order_link.appendChild(text_node)
#            column_node.appendChild(order_link)
#            row_node.appendChild(column_node)
#
#    def append_actions_to_row(self,node,widget,row_node):
#        #add column relative to actions
#        if (node['object'] in ['class','link_list','m2m']) :
#            column_node = widget.createElement('th')
#    #                        text_node = widget.createTextNode('actions')
#    #                        column_node.setAttribute('class','ordering_field')
#    #                        column_node.appendChild(text_node)
#            row_node.appendChild(column_node) 
#
#    def make_table_header(self,node,widget,node_type,table_fields):
#        table_header = widget.createElement('thead')
#        #table_node.setAttribute('class','%s_title_%s'%(node_type,selection_state))
#        row_node = widget.createElement('tr')
#        #add a col for displaying expander for each cell
#        cell_expander = widget.createElement('th')
#        img_node = widget.createElement('img')
#        #expander_image = '/media/images/%s_expander_square.png' % (node_type)
#        expander_image = '/media/images/node_expander_square.png'
#        img_node.setAttribute('src',expander_image)
#        img_node.setAttribute('class','dot')
#        cell_expander.appendChild(img_node)
#        row_node.appendChild(cell_expander)
#        self.append_field_labels(node,widget,table_fields,row_node)
#        self.append_actions_to_row(node,widget,row_node) 
#        table_header.appendChild(row_node)
#        return table_header
#    
#    def retrieve_cells_data(self,node):
#        #retrieve data of each cell
#        if not node['object'] in ['link_list','m2m'] :
#            index = node['index']
#            children = [k for k in self.nodes if (k['parent']['index'] == node['index'])]    
#        else :
#            index = node['index']
#            objects = self.tables[index]['paginator'].page(self.tables[index]['page']).object_list
#            children = list()
#            for obj in objects :
#                candidates = [k for k in self.nodes if (k['parent']['index'] == node['index']) and ((k['db_object'] == obj) or (k['db_object'] == cast_object_to_leaf_class(obj)))]
#                child = candidates[0]
#                children.append(child)
#            #children = [k for k in self.nodes if (k['parent']['index'] == node['index']) and (k['db_object'] in objects)]
#        return children,index
#
#    def make_table_body(self,node,widget,node_type,identifier,list_of_actions,in_expander,out_expander,table_fields,children,container_class,test):
#        table_body = widget.createElement('tbody')
#        n = 0
#        cycle = ('even','odd')
#        for child in children :
#            #access control data
#            db_object = child['db_object']
#            access_control = is_under_access_control(db_object.__class__)
#            can_delete = not access_control or is_deletable_by(db_object,self.user) 
#            can_modify = not access_control or is_editable_by(db_object,self.user)
#            #values corresponding to each column of the table
#            values = [{k['title']['original']:k['value']} for k in self.nodes if (k['object'] in ['value','property','fkey','link']) and (k['parent']['index'] == child['index'])]# and (k['title']['original'] in table_fields)]   
#            values_hr = [{k['title']['human_readable']:k['value']} for k in self.nodes if (k['object'] in ['value','property','fkey','link']) and (k['parent']['index'] == child['index'])]# and (k['title']['human_readable'] in table_fields) and (k['title']['human_readable'] != k['title']['original'])]
#            values.extend(values_hr)
#            value_dct = dict()
#            for value in values :
#                value_dct.update(value)
#            #adding expander relative to a child
#            if child['state'] == 'opened' :
#                child_action = 'close'
#            elif child['state'] == 'closed' :
#                child_action = 'open'
#            row_node = widget.createElement('tr')
#            row_node.setAttribute('class','row_%s' % (cycle[n%2])) 
#            cell_expander = widget.createElement('td')
#            if node['object'] in ['m2m','link_list'] :
#                delegate = child  
#            else :
#                delegate = child
#            #difference between fields and object attributes
#            child_detail = [k for k in self.nodes if (k['parent']['index'] == delegate['index'])]
#            child_detail = [k for k in child_detail if not ((k['title']['original'] in out_expander) or (k['title']['human_readable'] in out_expander))]
#            child_detail = [k for k in child_detail if (not ((k['title']['human_readable'] in table_fields) or (k['title']['original'] in table_fields)) or (k['title']['original'] in in_expander) or (k['title']['human_readable'] in in_expander))]
#            #remove duplications when a property overload a field name
#            child_detail = [k for k in child_detail if not (k['object'] in ['value','property']) or (not (k['title']['human_readable'] in table_fields) and not (k['title']['original'] in table_fields))]
#            if child_detail :  
#                link_node = widget.createElement('a')
#                link_node.setAttribute('href',self.admin_url + '?action=%s&widget_id=%s&node_id=%s'%(child_action,self.id,child['index']))
#                link_node.setAttribute('class','button')
#                img_node = widget.createElement('img')
#                #expander_image = '/media/images/%s_expander_%s.png' % (node_type,child['state'])
#                expander_image = '/media/images/node_expander_%s.png' % (child['state'])
#                img_node.setAttribute('src',expander_image)
#                link_node.appendChild(img_node)
#                cell_expander.appendChild(link_node)
#                cell_expander.setAttribute('class','expander_cell')
#            else :
#                img_node = widget.createElement('img')
#                img_node.setAttribute('class','dot')
#                #expander_image = '/media/images/%s_expander_square.png' % (node_type)
#                expander_image = '/media/images/node_expander_square.png'
#                img_node.setAttribute('src',expander_image)
#                cell_expander.appendChild(img_node)
#                cell_expander.setAttribute('class','expander_cell')
#            row_node.appendChild(cell_expander)
#            for field in table_fields :
#                column_node = widget.createElement('td')
#                if value_dct[field] and (value_dct[field].__class__.__name__ == 'ImageFieldFile') :
#                    image_node = widget.createElement('img')
#                    src = "/media/%s" % (value_dct[field])
#                    image_node.setAttribute('src',src)
#                    link_node = widget.createElement('a')
#                    link_node.setAttribute('href',src)
#                    link_node.appendChild(image_node)
#                    column_node.appendChild(link_node)
#                    column_node.setAttribute('class','image_node')
#                elif value_dct[field] and (value_dct[field].__class__.__name__ == 'FieldFile') :
#                    raise Exception('not implemented case')
#                    text_node = widget.createTextNode("%s" % value_dct[field])
#                    link_node = widget.createElement('a')
#                    href = "/media/%s" % (value_dct[field])
#                    link_node.setAttribute('href',href)
#                    link_node.appendChild(text_node)
#                    column_node.appendChild(link_node)
#                    column_node.setAttribute('class','link_node')
#                else :
#                    text_node = widget.createTextNode("%s" % value_dct[field])
#                    column_node.appendChild(text_node)
#                row_node.appendChild(column_node)
#            #add actions
#            column_node = widget.createElement('td')
#            column_node.setAttribute('width','70px')
#            if child['object'] == 'object' :
#                action = 'delete_object'
#                if not list_of_actions or (action in list_of_actions) :
#                    href = self.admin_url + '?action=%s&widget_id=%s&node_id=%s'%(action,self.id,child['index'])#,node['class'],node['id'])
#                    action_node = self.create_button(widget,action,href,identifier,can_delete)
#                    column_node.appendChild(action_node)
#                action = 'modify_object'
#                if not list_of_actions or (action in list_of_actions) :    
#                    href = self.admin_url + '?action=%s&widget_id=%s&node_id=%s'%(action,self.id,child['index'])
#                    action_node = self.create_button(widget,action,href,identifier,can_modify)
#                    column_node.appendChild(action_node)
#            elif child['object'] == 'link' :
#                child_parent = self.index[child['parent']['index']]
#                ancestor_node = self.index[child_parent['parent']['index']]
#                if child_parent['object'] == 'm2m' :
#                    is_required = False
#                    #is_required = ancestor_node['node']['objects'].hierarchy['many_to_many_fields'][parent_node['title']['original']]['is_required']
#                elif (child_parent['object'] == 'link_list') and not ancestor_node['object'] in ['link_list_subclass','m2m_subclass'] :
#                    field = ancestor_node['node']['dependent_classes'][child_parent['title']['original']]
#                    is_required = field['is_required']
#                else :
#                    parent_ancestor = self.index[ancestor_node['parent']['index']]
#                    if ancestor_node['object'] == 'm2m_subclass' :
#                        is_required = False
#                    else :
#                        field = parent_ancestor['node']['dependent_classes'][ancestor_node['title']['original']]
#                        is_required = field['is_required']
#                action = 'delete_object'
#                if not list_of_actions or (action in list_of_actions) :
#                    href = self.admin_url + '?action=%s&widget_id=%s&node_id=%s'%(action,self.id,child['index'])#,node['class'],node['id'])
#                    action_node = self.create_button(widget,action,href,identifier,can_delete)
#                    column_node.appendChild(action_node)
#                action = 'unlink_object'
#                if not is_required and (not list_of_actions or (action in list_of_actions)) :
#                    href = self.admin_url + '?action=%s&widget_id=%s&node_id=%s'%(action,self.id,child['index'])
#                    action_node = self.create_button(widget,action,href,identifier,can_modify)
#                    column_node.appendChild(action_node)
#                action = 'modify_object'
#                if not list_of_actions or (action in list_of_actions) :
#                    href = self.admin_url + '?action=%s&widget_id=%s&node_id=%s'%(action,self.id,child['index'])
#                    action_node = self.create_button(widget,action,href,identifier,can_modify)
#                    column_node.appendChild(action_node)    
#            row_node.appendChild(column_node)  
#            
#            
#            table_body.appendChild(row_node)
#            #create a new row containing details relative to an expanded row
#            if child['state'] == 'opened' :
#                row_node = widget.createElement('tr')
#                column_node = widget.createElement('td')
#                row_node.setAttribute('class','expanded_row')
#                column_node = widget.createElement('td')
#                column_node.setAttribute('colspan',"%s"%(len(table_fields)+1+int(test)))
#                column_node.setAttribute('class','cell_details')
#                #child container
#                container_class = "node_container_%s" % (child['state'])
#                child_container = widget.createElement('div')
#                child_id = "%s_%s" % (self.id,child['index'])
#                child_container.setAttribute('id','container_%s' % (child_id))
#                child_container.setIdAttribute('id')
#                column_node.appendChild(child_container)
#                row_node.appendChild(column_node)
#                table_body.appendChild(row_node)
#                #child_detail = [k for k in self.nodes if (k['parent']['index'] == child['index']) and not (k['title'] in table_fields)]
#                self.visit_nodes_recursively(widget,child_detail,child_container,False)
#            n += 1
#        return table_body
#    
#    def make_table_footer(self,node,widget,table_fields,index,test):
#        table_footer = widget.createElement('tfoot') 
#                     
#        #paginator
#        row = widget.createElement('tr') 
#        row.setAttribute('class','footer')
#        column = widget.createElement('td')
#        column.setAttribute('colspan',"%s"%(len(table_fields)+1+int(test))) 
#        paginator = widget.createElement('div')
#        paginator.setAttribute('class','paginator')
#        column.appendChild(paginator)
#        row.appendChild(column)
#        table_footer.appendChild(row)
#        #page numbers
#        center_div = widget.createElement('div')
#        center_div.setAttribute('class','counter')
#        n_pages = self.tables[index]['paginator'].num_pages
#        if n_pages > 1 :
#            for i in range(1,n_pages+1) :
#                link = widget.createElement('a')
#                if i == self.tables[index]['page'] :
#                    link.setAttribute('class','selected_page')
#                else :
#                    link.setAttribute('class','table_page')
#                link.setAttribute('href',self.admin_url + '?action=%s&widget_id=%s&node_id=%s&page=%s' % ('select_page',self.id,node['index'],i))
#                number = widget.createTextNode(str(i))
#                link.appendChild(number)
#                if center_div.hasChildNodes() :
#                    span = widget.createElement('span')
#                    separator = widget.createTextNode(' | ')
#                    span.appendChild(separator)
#                    center_div.appendChild(span)   
#                center_div.appendChild(link)     
#        else :
#            invisible_text = widget.createElement('br')
#            center_div.appendChild(invisible_text)
#                  
#        paginator.appendChild(center_div)
#        return table_footer
#    
#    def make_table(self,node,widget,node_type,identifier,list_of_actions,container_node,container_class,test):
#        if node['state'] == 'opened' :
#            hierarchy,expansion,in_expander,out_expander = self.prepare_table(node)
#            table_fields = self.get_table_fields(node,hierarchy,expansion)
#            cls = 'table_container' if (node_type != 'root_node') else 'root_table_container'
#            container_node.setAttribute('class',cls)
#            table_node = self.make_table_node(node,widget,identifier)
#            table_header = self.make_table_header(node,widget,node_type,table_fields)
#            table_node.appendChild(table_header)
#            children,index = self.retrieve_cells_data(node)
#            table_body = self.make_table_body(node,widget,node_type,identifier,list_of_actions,in_expander,out_expander,table_fields,children,container_class,test)
#            table_node.appendChild(table_body) 
#            table_footer = self.make_table_footer(node,widget,table_fields,index,test)
#            table_node.appendChild(table_footer) 
#        else :
#            table_node = widget.createTextNode(' ')
#        return table_node
#    
#    def visit_nodes_recursively(self,widget,nodes,destination,starting_point=True):   
#        for node in nodes :         
#            identifier,node_type,action,selection_state = self.init_node(node)
#            docnode = self.init_domnode(widget,identifier)
#            header_node = self.make_header(node,widget,node_type,selection_state,identifier)
#            title_node = self.make_title(node,widget,node_type,selection_state,identifier)
#            expander_node = self.make_expander(node,widget,node_type,action,identifier)
#            header_node.appendChild(expander_node)
#            header_node.appendChild(title_node)
#            list_of_actions = self.define_actions(node,widget,header_node,identifier)      
#            container_node,container_class = self.make_container(node,widget,node_type,identifier)               
#            self.append_header_and_container(docnode,header_node,container_node)
#            #create a table  
#            if node['table'] and (node['object'] in ['class','link_list','m2m']) :
#                test=True
#                table_node = self.make_table(node,widget,node_type,identifier,list_of_actions,container_node,container_class,test)             
#                container_node.appendChild(table_node)
#            else :
#                self.make_recursion(node,widget,container_node,container_class)
#            #finally append node to destination
#            destination.appendChild(docnode)
#    
#    def make_recursion(self,node,widget,container_node,container_class):
#        container_node.setAttribute('class',container_class)
#        #add children recursively to node if it is opened
#        if (node['state'] == 'opened') :
#            children = [k for k in self.nodes if (k['parent']['index'] == node['index'])] 
#            self.visit_nodes_recursively(widget,children,container_node)
#        else :
#            void_text = widget.createTextNode(' ')
#            container_node.appendChild(void_text)
#
#    def _flat_tree_representation(self,hierarchy,obj,parent_index=None,structure=None,starting_point=True):
#        if starting_point :
#            structure = hierarchy.hierarchic_representation(obj)
#        i = 0
##        if obj.__class__.__name__ == 'ScientificStructure' and obj.diminutive == 'sc2' :
##            raise Exception('test')
#        for node in structure :
#            extra_content = copy(structure[node]['extra_content'])
#            
#            extra_content['index'] = "%s.%s" % (parent_index,i)
#            extra_content['parent']['index'] = parent_index
#            if self.old_index :
#                if (extra_content['index'] in self.old_index) and (extra_content['type'] != 'leaf'):
#                    extra_content['state'] = self.old_index[extra_content['index']]['state']
##                elif (extra_content['type'] == 'leaf') and (self.index[parent_index]['node']['constraints']['limit_to_one_subclass']):
##                    extra_content['state'] = 'opened'
##                elif not (self.index[parent_index]['node']['constraints']['limit_to_one_subclass']) :
##                    extra_content['state'] = 'closed'    
##            else :
##                #find a replacement condition to test limit_to_one_subclass
##                if not self.index[parent_index]['node']['constraints']['limit_to_one_subclass'] :
##                    extra_content['state'] = 'closed'
#            if not self.already_exists(extra_content) :
#                self.nodes.append(extra_content)
#                self.index[extra_content['index']] = self.nodes[-1]
#            if (extra_content['object'] in ['fkey','link']) and (len(extra_content['can_create']) > 1) and (extra_content['db_object'].__class__.__name__ != 'ModelBase'):
#                extra_content['state'] = 'opened'
#                new_structure = structure[node]['content']
#                ancestor = extra_content['db_object']
#                intermediate = deepcopy(extra_content)
#                intermediate['index'] = "%s.0" % (extra_content['index'])
#                intermediate['parent']['index'] = extra_content['index']
#                intermediate['parent']['class'] = ancestor.__class__.__name__
#                intermediate['type'] = 'leaf'
#                #extra_content['state'] = 'closed'
#                intermediate['state'] = 'opened'
#                cast = cast_object_to_leaf_class(ancestor)
#                intermediate['db_object'] = cast
#                intermediate['class'] = cast.__class__.__name__
#                intermediate['object'] = 'subclass_header'
#                intermediate['title']['original'] = cast.__class__.__name__
#                intermediate['title']['human_readable'] = cast.__class__._meta.verbose_name.lower()
#                if not self.already_exists(intermediate) :
#                    self.nodes.append(intermediate)
#                    self.index[intermediate['index']] = self.nodes[-1]  
#                if isinstance(structure[node]['content'],dict) :
#                    extra_content['type'] = 'group'
#                    self._flat_tree_representation(hierarchy,obj,intermediate['index'],new_structure,starting_point=False)     
#                else :
#                    intermediate['value'] = cast.__unicode__()
#            elif isinstance(structure[node]['content'],dict) :  
#                extra_content['state'] = 'opened' 
#                new_structure = structure[node]['content']
#                self._flat_tree_representation(hierarchy,obj,extra_content['index'],new_structure,starting_point=False)   
#            elif isinstance(structure[node]['content'],list) :
#                extra_content['state'] = 'opened'
#                n = self.index["%s.%s" % (parent_index,i)]
#                if not n['table'] :
#                    index = extra_content['index']
#                    j = 0
#                    for item in structure[node]['content'] :
#                        extra_content = deepcopy(item['extra_content'])
#                        extra_content['index'] = "%s.%s.%s" % (parent_index,i,j)
#                        extra_content['parent']['index'] = index
#                        extra_content['state'] = 'closed' if (not self.old_index) or not (extra_content['index'] in self.old_index) else self.old_index[extra_content['index']]['state']
#                        if not self.already_exists(extra_content) :
#                            self.nodes.append(extra_content)
#                            self.index[extra_content['index']] = self.nodes[-1]
#                        if isinstance(item['content'],dict) :
#                            new_structure = item['content']
#                            self._flat_tree_representation(hierarchy,obj,extra_content['index'],new_structure,starting_point=False)
#                        j += 1
#                else :
#                    self.expand_link_node(n,n['table'])
#                    self.expand_class_node(n,n['table'])
#            i += 1
#
#        if starting_point :
#            return
#    
#    def index_weight(self,dct):
#        values = [int(k) for k in dct['index'].split('.')]
#        weight = 1
#        for value in values :
#            total = value * weight
#            weight *= 10
#        return total
#
#    def find_page(self,node,instance):
#        manager = self.get_manager(node)
#        objects = manager.all() 
#        if is_under_access_control(manager.model) :
#            objects = get_accessible_by(objects,self.user)  
#        lst = [cast_object_to_leaf_class(k) for k in objects if (cast_object_to_leaf_class(k).__class__ == instance.__class__)]
#        lst.sort(key=lambda x:self.retrieve_property_value(x,node['index'],node['node']['constraints']['properties'],self.tables[node['index']]['order_by']))
#        pagination = node['node']['constraints']['table']['pagination']
#        if self.tables[node['index']]['ordering'] == 'descending' :
#            lst.reverse()
#        a= len(lst)
#        index = lst.index(instance) + 1
#        page = index / pagination
#        if page < 1 :
#            page = 1
#        self.tables[node['index']]['page'] = page
#
#class ObjectViewWidget(GenericWidget):
#    """A generic widget to display the hierarchical representation of an object."""
#    
#    def __init__(self,id,obj,description,default_state='closed',user=None,width="auto"):
#        super(ObjectViewWidget,self).__init__(id,description,default_state,user,width)
#        self.obj = obj
#        self.hierarchy = HierarchicView(self.obj.__class__.__name__,self.obj.__class__.__module__,constraints=self.description,extra_content=True,user=self.user)
#        self.tables = SortedDict()
#        self.old_index = None
#        self.old_tables = None
#        self.nodes,self.index = self.init_tree()
#        self._flat_tree_representation(self.hierarchy,self.obj,self.nodes[-1]['index'])
#        
#    def init_tree(self):
#        flat_tree = list()
#        index = SortedDict()
#        node_index = '0'
#        dct = deepcopy(node_template)
#        dct['index'] = node_index
#        dct['class'] = self.obj.__class__.__name__
#        dct['id'] = self.obj.pk
#        dct['db_object'] = self.obj
#        dct['title']['human_readable'] = "%s : %s" % (self.obj.__class__.__name__,self.obj.__unicode__())
#        dct['title']['original'] = "%s : %s" % (self.obj.__class__.__name__,self.obj.__unicode__())
#        dct['value'] = self.obj.__unicode__()
#        dct['type'] = 'group'
#        dct['state'] = self.default_state
#        dct['node'] = self.description[self.obj.__class__.__name__]
#        dct['node']['dependent_classes'] = get_dependencies(self.obj.__class__)
#        dct['object'] = 'object'
#        dct['parent']['class'] = self.obj.__class__.__name__
#        flat_tree.append(dct)
#        index[node_index] = flat_tree[-1]
#        return flat_tree,index
#        
#    def expand_object_node(self,node):
#        pass
#
#def get_custom_structure(description,module_name=None,modules=None,classes=None,index_table=None,index=None,starting_point=True,shunt_models=True,start_module=None,compress=False,extra_content=False,user=None):
#    """Organise project applications, modules and classes in a hierarchical manner defined by a description dictionary."""
#    if starting_point :
#        modules = list()
#        classes = list()
#        index_table = list()
#        index = []
#    
#    for item in description :
#        assert description[item].has_key('position'), "position not specified for module %s" % (module_name)
#        new_index = copy(index)
#        new_index.append(description[item]['position'])
#            
#        if starting_point :
#            new_module_name = item
#            start_module = None
#        else :
#            new_module_name = "%s.%s" % (module_name,item)
#            if (len(module_name.split('.')) == 1) and (not start_module) :
#                start_module = "%s.%s" % (module_name,item)    
#        
#        if description[item].has_key('modules') and isinstance(description[item]['modules'],dict) :   
#            get_custom_structure(description[item]['modules'],new_module_name,modules,classes,index_table,new_index,False,shunt_models,start_module,user=user)
#        elif description[item].has_key('classes') and isinstance(description[item]['classes'],dict) :
#            if not starting_point :
#                splitted_start_module = start_module.split('.')
#                index_of_models = len(splitted_start_module)
#                raw_name = "%s.%s" % (module_name,item) 
#                splitted_raw_name = raw_name.split(".")
#                if not (('models' in splitted_raw_name) and (splitted_raw_name.index('models') == len(splitted_start_module))) :
#                    splitted_raw_name.insert(index_of_models,'models')
#                corrected_module_name = '.'.join(splitted_raw_name)
#            elif not description[item].has_key('modules') :
#                corrected_module_name = new_module_name + ".models"
#            modules.append(corrected_module_name)
#            for cls in description[item]['classes'] :
#                class_name = "%s.%s" % (corrected_module_name,cls)
#                assert description[item]['classes'][cls].has_key('position'), "position not specified for %s" % (class_name)
#                assert description[item]['classes'][cls].has_key('constraints'), "constraints not specified for %s" % (class_name)
#                classes.append(class_name)
#                new_class_index = copy(new_index)
#                new_class_index.append(description[item]['classes'][cls]['position'])
#                constraints = description[item]['classes'][cls]['constraints']
#                index_table.append((class_name,new_class_index,constraints))
#    
#    if starting_point :
#        index_table.sort(key=lambda x:x[1])
#        hierarchy = get_class_hierarchy(user=user,modules_filter=modules,classes_filter=classes,order_filter=index_table,compress=compress,extra_content=extra_content)
#        return hierarchy    
#
#class MenuWidget(GenericWidget):
#    """A widget to display classes in a menu."""
#    def __init__(self,id,description,as_admin=False,default_state='closed',user=None,width=None):
#        super(MenuWidget,self).__init__(id,description,default_state,user,width)
#        self.as_admin = as_admin
#        self.hierarchy = self.get_custom_structure()
#        self.nodes,self.index,self.tables = self.init_tree()
#        self.old_index = None
#        self.old_tables = None
#    
#    def browse_class(self,names,class_name,modules,classes,new_index,index_table,new_section,is_class=False):
#        assert names[class_name].has_key('module'),"class %s module not specified" % (class_name)
#        module_name = names[class_name]['module']
#        modules.append(module_name)
#        complete_class_name = "%s.%s" % (module_name,class_name)
#        assert names[class_name].has_key('position'), "position not specified for %s" % (complete_class_name)
#        assert names[class_name].has_key('constraints'), "constraints not specified for %s" % (complete_class_name)
#        classes.append(complete_class_name)
#        new_class_index = copy(new_index)
#        new_class_index.append(names[class_name]['position'])
#        constraints = names[class_name]['constraints']
#        index_table.append((complete_class_name,new_class_index,constraints,new_section,is_class))
#    
#    def get_custom_structure(self,index=None,description=None,section=None,sections=None,modules=None,classes=None,index_table=None,starting_point=True):
#        """Organise project applications, modules and classes in a hierarchical manner."""
#        if starting_point :
#            sections = list()
#            modules = list()
#            classes = list()
#            index_table = list()
#            index = []
#            description = self.description
#        
#        for item in description :
#            if description[item].has_key('classes') or description[item].has_key('modules') :
#                #verify if position parameter is in the description
#                assert description[item].has_key('position'), "position not specified for node %s" % (item)
#                #create a new index to make possible sorting of menu nodes
#                new_index = copy(index)
#                new_index.append(description[item]['position'])
#                new_section = "%s.%s" % (section,item) if section else item
#                sections.append(new_section)
#                if description[item].has_key('modules') and isinstance(description[item]['modules'],dict) :
#                    self.get_custom_structure(new_index,description[item]['modules'],new_section,sections,modules,classes,index_table,False)
#                if description[item].has_key('classes') and isinstance(description[item]['classes'],dict) :
#                    names = description[item]['classes']
#                    for class_name in names :
#                        self.browse_class(names,class_name,modules,classes,new_index,index_table,new_section)
#            elif starting_point :
#                new_index = copy(index)
#                new_section = item
#                is_class = True
#                self.browse_class(description,item,modules,classes,new_index,index_table,new_section,True)
#                
#        
#        if starting_point :
#            index_table.sort(key=lambda x:x[1])
#            if not self.as_admin :
#                hierarchy = get_menu_hierarchy(sections,modules_filter=modules,classes_filter=classes,order_filter=index_table,extra_content=self.extra_content,user=self.user)
#            else :
#                hierarchy = get_class_hierarchy(modules_filter=modules,classes_filter=classes,order_filter=index_table,shunt_models=True,compress=True,extra_content=self.extra_content,user=self.user)    
#            return hierarchy
#    
#    def init_class(self,cls,structure,tables,forced_index,parent_index,flat_tree,index,base_class=False):
#        manager = cls.objects
#        objects = manager.all()
#        if is_under_access_control(manager.model) :
#            objects = get_accessible_by(objects,self.user)
#        if objects.count() :
#            node_type = 'group'
#        else :
#            node_type = 'leaf'
#        if structure['constraints'] and structure['constraints'].has_key('table') and  structure['constraints']['table'] :
#            table = structure['constraints']['table']
#            #init table index
#            tables[forced_index] = dict()
#            tables[forced_index]['page'] = 1   
#            tables[forced_index]['order_by'],tables[forced_index]['ordering'] = self.define_order(structure,table)    
#        else :
#            table = None
#        subclasses = [k for k in get_subclasses_recursively(cls,strict=False)]
#        hr_title = cls._meta.verbose_name_plural.capitalize()
#        if (cls.__name__ == structure['class'].__name__) and structure['constraints']['display_base_class'] and base_class :
#            cls_name = cls.__name__
#            hr_title = "All %s" % hr_title
#        else :
#            cls_name = None
#        dct = {'index':forced_index,
#               'class':cls.__name__,
#               'id':None,
#               'db_object':cls,
#               'parent':{'id':None,
#                         'class':cls_name,
#                         'index':parent_index},
#               'can_create':subclasses,
#               'can_be_deleted':False,
#               'can_be_updated':False,
#               'title':{'human_readable':hr_title,
#                        'original':cls._meta.object_name},
#               'value':None,
#               'type':node_type,
#               'state':'closed',
#               'table':table,
#               'node':structure,
#               'object':'class'
#              }
#        
#        flat_tree.append(dct)
#        index[forced_index] = flat_tree[-1]
#    
#    def get_dependent_classes(self,cls,subcls,structure):
#        classes = get_subclasses_recursively(cls)
#        delegate = structure['objects'].hierarchy['subclasses']
#        for subclass in classes :
#            name = subclass.__name__.lower()
#            delegate = delegate[name]
#            if delegate.has_key('subclasses') :
#                delegate = delegate['subclasses']
#            else :
#                break
#        return delegate['dependent_classes']
#            
#    def init_tree(self,structure=None,flat_tree=None,index=None,tables=None,parent_index=None,starting_point=True,forced_index=None,start_index=0):
#        if starting_point :
#            flat_tree = list()
#            index = SortedDict()
#            tables = SortedDict()
#            structure = self.hierarchy
#        
#        is_class = self.node_is_class(structure)
#        if not is_class :
#            i = start_index
#            for node in structure :
#                #detect the type of node
#                
#                is_leaf_class = structure[node].has_key('class') and starting_point
#                if not is_leaf_class :
#                    is_leaf_module = structure[node].has_key('classes') 
#                    if not is_leaf_module :
#                        if len(structure[node]) > 0 :
#                            node_type = 'group'
#                        else :
#                            node_type = 'leaf'
#                    else :
#                        if (len(structure[node]['classes']) > 0) :
#                            node_type = 'group'
#                        else :
#                            node_type = 'leaf'
#                    if parent_index :
#                        node_index = "%s.%s" % (parent_index,i)
#                    else :
#                        node_index = str(i)
#                    dct = {'index':node_index,
#                           'class':'module',
#                           'id':None,
#                           'db_object':None if not is_leaf_class else cls,
#                           'parent':{'id':None,
#                                     'class':None,
#                                     'index':parent_index},
#                           'can_create':[],
#                           'can_be_deleted':False,
#                           'can_be_updated':False,
#                           'title':{'human_readable':node,'original':node},
#                           'value':None,
#                           'type':node_type,
#                           'state':self.default_state,
#                           'table':None,
#                           'node':structure[node],
#                           'object':'module'
#                          }
#                    flat_tree.append(dct)
#                    index[node_index] = flat_tree[-1]
#                    if isinstance(structure[node],dict) :
#                        j = 0
#                        if (structure[node].has_key('classes')) : 
#                            new_parent_index = dct['index']
#                            for cls in structure[node]['classes'] :
#                                new_structure = structure[node]['classes'][cls]
#                                forced_index = "%s.%s" % (new_parent_index,j)
#                                self.init_tree(new_structure,flat_tree,index,tables,new_parent_index,False,forced_index)
#                                j += 1
#                        if (structure[node].has_key('modules')) :
#                            new_parent_index = dct['index']
#                            new_structure = structure[node]['modules']
#                            self.init_tree(new_structure,flat_tree,index,tables,new_parent_index,False,start_index=j)   
#                    i += 1
#                else :
#                    new_structure = structure[node]
#                    self.init_tree(new_structure,flat_tree,index,tables,None,False,forced_index=str(i))
#                    i += 1             
#        else :
#            cls = structure['class']
#            
#            subclasses = [k for k in get_subclasses_recursively(cls) if not (k.__name__ in structure['constraints']['excluded_subclasses'])]
#            subclasses.sort(key=lambda x:x.__name__)
#            if not subclasses :
#                self.init_class(cls,structure,tables,forced_index,parent_index,flat_tree,index)   
#            else :
#                #cls_hierarchy = HierarchicView(cls.__name__,cls.__module__,select_foreign_models=True,constraints={cls.__name__:structure},extra_content=True,user=self.user,complete_constraints=True)
#                if structure['constraints']['display_base_class']:
#                    subclasses.insert(0,cls)
#                self.init_class(cls,structure,tables,forced_index,parent_index,flat_tree,index)
#                flat_tree[-1]['type'] = 'group'
#                flat_tree[-1]['state'] = 'closed'
#                flat_tree[-1]['object'] = 'root_class'
#                new_parent_index = flat_tree[-1]['index']
#                i = 0
#                for subclass in subclasses :
#                    new_forced_index = "%s.%s" % (new_parent_index,i) 
#                    if subclass != cls :
#                        new_constraints = structure['constraints']['links'][subclass.__name__]['constraints']
#                        base_class = False
#                        chain = get_parents_recursively(subclass)
#                        chain.reverse()
#                        h = structure['objects'].hierarchy
#                        for item in chain[1:] :
#                            h = h['subclasses'][item.__name__.lower()]
#                        if (cls.__name__ != subclass.__name__) :
#                            h = h['subclasses'][subclass.__name__.lower()]
##                        a = structure['objects'].hierarchy['subclasses']
##                        h = structure['objects'].hierarchy['subclasses'][subclass.__name__.lower()]
#                        #structure['objects'].extend_with_parent_constraints(cls,subclass,structure['constraints'],new_constraints)
#                    else :
#                        new_constraints = structure['constraints']
#                        base_class = True
#                        h = None
#                    dependent_classes = self.get_dependent_classes(cls,subclass,structure)
#                    new_structure = {'class':subclass,
#                                     'constraints':new_constraints,
#                                     'dependent_classes':dependent_classes} 
#                    new_structure['objects'] = HierarchicView(subclass.__name__,subclass.__module__,select_foreign_models=True,constraints={subclass.__name__:new_structure},extra_content=True,user=self.user,complete_constraints=False,hierarchy=h)
#                    
#                    self.init_class(subclass,new_structure,tables,new_forced_index,new_parent_index,flat_tree,index,base_class=base_class) 
#                    i += 1   
#                    
#        if starting_point :
#            return flat_tree,index,tables
#    
#class AdminWidget(GenericWidget):
#    """A generic widget to display database data."""
#    def __init__(self,id,description,shunt_models=True,compress=False,default_state='closed',user=None):
#        super(AdminWidget,self).__init__(id,description,default_state,user)
#        self.shunt_models = shunt_models
#        self.compress = compress
#        self.hierarchy = self.get_custom_structure()#get_custom_structure(self.description,compress=self.compress,extra_content=self.extra_content)#self.get_custom_structure()
#        self.nodes,self.index,self.tables = self.init_tree()
#
#    def get_custom_structure(self,module_name=None,modules=None,classes=None,index_table=None,starting_point=True,start_module=None):
#        """Organise project applications, modules and classes in a hierarchical manner."""
#        if starting_point :
#            modules = list()
#            classes = list()
#            index_table = list()
#            index = []
#        
#        for item in self.description :
#            assert self.description[item].has_key('position'), "position not specified for module %s" % (module_name)
#            new_index = copy(index)
#            new_index.append(self.description[item]['position'])
#                
#            if starting_point :
#                new_module_name = item
#                start_module = None
#            else :
#                new_module_name = "%s.%s" % (module_name,item)
#                if (len(module_name.split('.')) == 1) and (not start_module) :
#                    start_module = "%s.%s" % (module_name,item)    
#            
#            if self.description[item].has_key('modules') and isinstance(self.description[item]['modules'],dict) :   
#                get_custom_structure(self.description[item]['modules'],new_module_name,modules,classes,index_table,new_index,False,self.shunt_models,start_module,user=self.user)
#            elif self.description[item].has_key('classes') and isinstance(self.description[item]['classes'],dict) :
#                if not starting_point :
#                    splitted_start_module = start_module.split('.')
#                    index_of_models = len(splitted_start_module)
#                    raw_name = "%s.%s" % (module_name,item) 
#                    splitted_raw_name = raw_name.split(".")
#                    if not (('models' in splitted_raw_name) and (splitted_raw_name.index('models') == len(splitted_start_module))) :
#                        splitted_raw_name.insert(index_of_models,'models')
#                    corrected_module_name = '.'.join(splitted_raw_name)
#                elif not self.description[item].has_key('modules') :
#                    corrected_module_name = new_module_name + ".models"
#                modules.append(corrected_module_name)
#                for cls in self.description[item]['classes'] :
#                    class_name = "%s.%s" % (corrected_module_name,cls)
#                    assert self.description[item]['classes'][cls].has_key('position'), "position not specified for %s" % (class_name)
#                    assert self.description[item]['classes'][cls].has_key('constraints'), "constraints not specified for %s" % (class_name)
#                    classes.append(class_name)
#                    new_class_index = copy(new_index)
#                    new_class_index.append(self.description[item]['classes'][cls]['position'])
#                    constraints = self.description[item]['classes'][cls]['constraints']
#                    index_table.append((class_name,new_class_index,constraints))
#        
#        if starting_point :
#            index_table.sort(key=lambda x:x[1])
#            hierarchy = get_class_hierarchy(modules_filter=modules,classes_filter=classes,order_filter=index_table,compress=self.compress,extra_content=self.extra_content,user=self.user)
#            return hierarchy
#    
#    def init_class(self,cls,structure,tables,forced_index,parent_index,flat_tree,index):
#        manager = cls.objects
#        objects = manager.all()
#        if is_under_access_control(manager.model) :
#            objects = get_accessible_by(objects,self.user)
#        if objects.count() :
#            node_type = 'group'
#        else :
#            node_type = 'leaf'
#        if structure['constraints'] and structure['constraints'].has_key('table') and  structure['constraints']['table'] :
#            table = structure['constraints']['table']
#            #init table index
#            tables[forced_index] = dict()
#            tables[forced_index]['page'] = 1   
#            tables[forced_index]['order_by'] = table['fields'][0] if table['fields'] else structure['objects'].hierarchy['fields'][0] 
#            tables[forced_index]['ordering'] = 'ascending'
#        else :
#            table = None
#        subclasses = [k for k in get_subclasses_recursively(cls,strict=False)]
#        
#        dct = {'index':forced_index,
#               'class':cls.__name__,
#               'id':None,
#               'db_object':cls,
#               'parent':{'id':None,
#                         'class':None,
#                         'index':parent_index},
#               'can_create':subclasses,
#               'can_be_deleted':False,
#               'can_be_updated':False,
#               'title':{'human_readable':cls._meta.verbose_name_plural.capitalize(),
#                        'original':cls._meta.object_name},
#               'value':None,
#               'type':node_type,
#               'state':'closed',
#               'table':table,
#               'node':structure,
#               'object':'class'
#              }
#        flat_tree.append(dct)
#        index[forced_index] = flat_tree[-1]
#    
#    def init_tree(self,structure=None,flat_tree=None,index=None,tables=None,parent_index=None,starting_point=True,forced_index=None):
#        if starting_point :
#            flat_tree = list()
#            index = SortedDict()
#            tables = SortedDict()
#            structure = self.hierarchy
#        
#        is_class = self.node_is_class(structure)
#        if not is_class :
#            i = 0
#            for node in structure :
#                #detect the type of node
#                is_leaf_module = structure[node].has_key('classes')
#                if not is_leaf_module :
#                    if len(structure[node]) > 0 :
#                        node_type = 'group'
#                    else :
#                        node_type = 'leaf'
#                else :
#                    if len(structure[node]['classes']) > 0 :
#                        node_type = 'group'
#                    else :
#                        node_type = 'leaf'
#                if parent_index :
#                    node_index = "%s.%s" % (parent_index,i)
#                else :
#                    node_index = str(i)
#                dct = {'index':node_index,
#                       'class':'module',
#                       'id':None,
#                       'db_object':None,
#                       'parent':{'id':None,
#                                 'class':None,
#                                 'index':parent_index},
#                       'can_create':[],
#                       'can_be_deleted':False,
#                       'can_be_updated':False,
#                       'title':{'human_readable':node,'original':node},
#                       'value':None,
#                       'type':node_type,
#                       'state':self.default_state,
#                       'table':None,
#                       'node':structure[node],
#                       'object':'module'
#                      }
#                flat_tree.append(dct)
#                index[node_index] = flat_tree[-1]
#                
#                if isinstance(structure[node],dict) :
#                    if (not structure[node].has_key('classes')) :
#                        new_parent_index = dct['index']
#                        new_structure = structure[node]
#                        self.init_tree(new_structure,flat_tree,index,tables,new_parent_index,False)
#                    else : 
#                        new_parent_index = dct['index']
#                        j = 0
#                        for cls in structure[node]['classes'] :
#                            new_structure = structure[node]['classes'][cls]
#                            forced_index = "%s.%s" % (new_parent_index,j)
#                            self.init_tree(new_structure,flat_tree,index,tables,new_parent_index,False,forced_index)
#                            j += 1
#                i += 1
#        else :
#            cls = structure['class']
#            subclasses = get_subclasses_recursively(cls)
#            subclasses.sort(key=lambda x:x.__name__)
#            
#            if not subclasses :
#                self.init_class(cls,structure,tables,forced_index,parent_index,flat_tree,index)    
#            else :
#                self.init_class(cls,structure,tables,forced_index,parent_index,flat_tree,index)
#                flat_tree[-1]['type'] = 'group'
#                flat_tree[-1]['state'] = 'closed'
#                flat_tree[-1]['object'] = 'root_class'
#                new_parent_index = flat_tree[-1]['index']
#                i = 0
#                for subclass in subclasses :
#                    new_forced_index = "%s.%s" % (new_parent_index,i) 
#                    new_constraints = deepcopy(constraints_template)
#                    structure['objects'].extend_with_parent_constraints(cls,subclass,structure['constraints'],new_constraints)
#                    new_structure = {'class':subclass,'constraints':new_constraints,'dependent_classes':structure['objects'].hierarchy['subclasses'][subclass.__name__.lower()]['dependent_classes']} 
#                    new_structure['objects'] = HierarchicView(subclass.__name__,subclass.__module__,select_foreign_models=True,constraints={subclass.__name__:new_structure},extra_content=True,user=self.user)
#                    self.init_class(subclass,new_structure,tables,new_forced_index,new_parent_index,flat_tree,index)
#                    i += 1   
#        if starting_point :
#            return flat_tree,index,tables
