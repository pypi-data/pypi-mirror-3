#encoding:utf-8
from copy import deepcopy

field_constraints = {
     'tableconstraint':{
         'displayed_in_navigator':False,
         'form':'helmholtz.editor.forms.editor.FieldForm',
         'actions':[
             {'name':'A'},
             {'name':'M'},
             {'name':'D'},
         ],
         'displayed_in_navigator':False,
         'shunt':True,
         'in_header':[
             {'field':{'identifier':'id'}},
             {'field':{'identifier':'identifier'}},
             {'field':{'identifier':'verbose_name'}},
         ],
         'width':'600px',
         'pagination':25
     }
}

expansion = {
    'force':True,
    'content_type':{
       'app_label':'editor',
       'model':'field'
    },
    'position':1,
    'constraints':[
        field_constraints
    ]
}

subfield_constraints = {
     'tableconstraint':{
         'displayed_in_navigator':False,
         'form':'helmholtz.editor.forms.editor.FieldForm',
         'actions':[
             {'name':'A'},
             {'name':'M'},
             {'name':'D'},
         ],
         'displayed_in_navigator':False,
         'shunt':True,
         'in_header':[
             {'field':{'identifier':'id'}},
             {'field':{'identifier':'identifier'}},
             {'field':{'identifier':'verbose_name'}},
         ],
         'width':'500px',
         'pagination':25
     }
}

subfield = {
    'force':True,
    'content_type':{
       'app_label':'editor',
       'model':'field'
    },
    'position':1,
    'constraints':[
        subfield_constraints
    ]
}

header_field_constraints = {
     'tableconstraint':{
         'displayed_in_navigator':False,
         'form':'helmholtz.editor.forms.editor.FieldForm',
         'actions':[
             {'name':'A'},
             {'name':'M'},
             {'name':'D'},
         ],
         'displayed_in_navigator':False,
         'shunt':False,
         'in_expansion':[
             {'field':{'identifier':'subfields'}}
         ],
         'in_header':[
             {'field':{'identifier':'id'}},
             {'field':{'identifier':'identifier'}},
             {'field':{'identifier':'verbose_name'}},
             {'field':{'identifier':'subfields.count', 'verbose_name':'subfields'}},
         ],
         'width':'600px',
         'pagination':25
     }
}

header = {
    'force':True,
    'content_type':{
       'app_label':'editor',
       'model':'field'
    },
    'position':1,
    'constraints':[
        header_field_constraints
    ],
    'children':[
        {'entity':subfield},
    ]
}

base_constraint = {
    'content_type':{
       'app_label':'editor',
       'model':'constraint'
    },
    'position':1,
    'constraints':[
        {
         'form':'helmholtz.editor.forms.editor.ConstraintForm',
         'display_base_class':True,
         'max_objects':1,
         'actions':[
             {'name':'A'},
             {'name':'M'},
             {'name':'D'},
         ],
         'shunt':False,
         'in_expansion':[
             {'field':{'identifier':'id'}},
             {'field':{'identifier':'form'}},
             {'field':{'identifier':'shunt'}},
             {'field':{'identifier':'displayed_in_navigator'}},
             {'field':{'identifier':'max_objects'}},
             {'field':{'identifier':'display_subclasses'}},
             {'field':{'identifier':'display_base_classes'}},
             {'field':{'identifier':'actions'}},
             {'field':{'identifier':'in_expansion'}},
             {'field':{'identifier':'excluded_subclasses'}},
         ]
        }    
    ],
    'children':[
        {'entity':deepcopy(expansion)}
    ]
}

table_constraint = {
    'content_type':{
       'app_label':'editor',
       'model':'tableconstraint'
    },
    'position':2,
    'constraints':[
        {
        'shunt':False,
        'max_objects':1,
        'form':'helmholtz.editor.forms.editor.TableConstraintForm',
        'in_expansion':[
             {'field':{'identifier':'id'}},
             {'field':{'identifier':'form'}},
             {'field':{'identifier':'shunt'}},
             {'field':{'identifier':'displayed_in_navigator'}},
             {'field':{'identifier':'max_objects'}},
             {'field':{'identifier':'display_subclasses'}},
             {'field':{'identifier':'display_base_classes'}},
             {'field':{'identifier':'width'}},
             {'field':{'identifier':'pagination'}},
             {'field':{'identifier':'actions'}},
             {'field':{'identifier':'in_expansion'}},
             {'field':{'identifier':'in_header'}},
             {'field':{'identifier':'excluded_subclasses'}},
         ]
        }
    ],
    'children':[
        {'entity':deepcopy(expansion), 'field_name':'in_expansion'},
        {'entity':deepcopy(header), 'field_name':'in_header'}
    ]
}

constraint = {
    'content_type':{
       'app_label':'editor',
       'model':'constraint'
    },
    'position':1,
    'constraints':[
        {
         'displayed_in_navigator':False,
         'form':'helmholtz.editor.forms.editor.ConstraintForm',
         'display_base_class':True,
         'actions':[
             {'name':'A'},
             {'name':'M'},
             {'name':'D'},
         ],
         'displayed_in_navigator':False,
         'shunt':False,
         'max_objects':1,
        }
    ],
    'children':[
        {'entity':base_constraint},
        {'entity':table_constraint}    
    ]
}

section_constraints = {
    'form':'helmholtz.editor.forms.editor.SectionForm',
    'displayed_in_navigator':False,
    'shunt':False,
#    'hierarchy':True,
#    'displayed_in_navigator':False,
#    'display_base_class':False,
    'excluded_subclasses':[
        {'app_label':'editor', 'model':'view'},
    ],
    'actions':[
        {'name':'A'},
        {'name':'M'},
        {'name':'D'},
    ],
    'in_expansion':[
        {'field':{'identifier':'id'}},
        {'field':{'identifier':'children'}}
    ]
}

section = {
    'content_type':{
       'app_label':'editor',
       'model':'section'
    },
    'position':1,
    'constraints':[
        section_constraints
    ]
}

entity_constraints = {
    'form':'helmholtz.editor.forms.editor.EntityForm',
    'displayed_in_navigator':False,
    'shunt':False,
#    'hierarchy':True,
#    'displayed_in_navigator':False,
#    'display_base_class':False,
    'excluded_subclasses':[
        {'app_label':'editor', 'model':'view'},
        #{'app_label':'editor', 'model':'section'},
    ],
    'actions':[
        {'name':'A'},
        {'name':'M'},
        {'name':'D'},
    ],
    'in_expansion':[
        {'field':{'identifier':'id'}},
        {'field':{'identifier':'constraints'}},
        {'field':{'identifier':'children'}}
    ]
}

node = {
    'content_type':{
       'app_label':'editor',
       'model':'node'
    },
    'position':2,
    'constraints':[
        {
         'actions':[
             {'name':'A'},
             {'name':'M'},
             {'name':'D'},
         ],
         'displayed_in_navigator':False,
         'display_base_class':False,
         'excluded_subclasses':[
             {'app_label':'editor', 'model':'view'},
             {'app_label':'editor', 'model':'section'},
         ],
         'in_expansion':[
             {'field':{'identifier':'id'}},
             {'field':{'identifier':'position'}},
             {'field':{'identifier':'constraints'}},
             {'field':{'identifier':'children'}},
         ]
        }
    ],
    'children':[
        {'entity':deepcopy(constraint)},
    ]
}

entity = {
    'content_type':{
       'app_label':'editor',
       'model':'entity'
    },
    'position':1,
    'constraints':[
        entity_constraints
    ],
    'children':[
        {'entity':deepcopy(constraint)},
        {'entity':node},
    ]
}

node = {
    'content_type':{
       'app_label':'editor',
       'model':'node'
    },
    'position':1,
    'constraints':[
        {
         'actions':[
             {'name':'A'},
             {'name':'M'},
             {'name':'D'},
         ],
         'hierarchy':True,
         'displayed_in_navigator':False,
         'display_base_class':False,
         'excluded_subclasses':[
             {'app_label':'editor', 'model':'view'},
         ],
         'in_expansion':[
             {'field':{'identifier':'id'}},
             {'field':{'identifier':'position'}},
             {'field':{'identifier':'constraints'}},
             {'field':{'identifier':'children'}},
         ]
        }
    ],
    'children':[
        {'entity':section},
        {'entity':entity},
        {'entity':deepcopy(constraint)},
    ]
}

view = {
    'content_type':{
       'app_label':'editor',
       'model':'view'
    },
    'position':1,
    'constraints':[
        {
         'tableconstraint':{
             'form':'helmholtz.editor.forms.editor.ViewForm',
             'displayed_in_navigator':False,
             'shunt':False,
             'in_expansion':[
                 {'field':{'identifier':'children'}},
             ],
             'in_header':[
                 {'field':{'identifier':'id'}},
                 {'field':{'identifier':'name'}},
                 {'field':{'identifier':'update'}},
                 {'field':{'identifier':'children.count', 'verbose_name':'sections'}},
             ],
             'width':'900px',
             'pagination':25
         }
        }
    ],
    'children':[
        {'entity':node}    
    ]
}
