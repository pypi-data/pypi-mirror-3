derived_constraints = [
    {'tableconstraint':{
         'shunt':True,
         'actions':[
             {'name':'A'},
             {'name':'M'},
             {'name':'D'}
         ],
         'displayed_in_navigator':False,
         'form':'helmholtz.editor.forms.units.DerivedUnitForm',
         'in_header':[
             {'field':{'identifier':'name'}},
             {'field':{'identifier':'symbol'}},
         ],
         'width':"500px",
         'pagination':50
     }
    }
]

derived = {
    'content_type':{
       'app_label':'units',
       'model':'derivedunit'
    },
    'position':0,
    'constraints':derived_constraints,
}

unit_constraints = [
    {'tableconstraint':{
         'displayed_in_navigator':False,
         'form':'helmholtz.editor.forms.units.BaseUnitForm',
         'in_header':[
             {'field':{'identifier':'name'}},
             {'field':{'identifier':'symbol'}},
             {'field':{'identifier':'physical_meaning'}},
             {'field':{'identifier':'math_symbol'}},
             {'field':{'identifier':'derivedunit_set.count', 'verbose_name':'derived units'}},
         ],
         'in_expansion':[
             {'field':{'identifier':'derivedunit_set'}}   
         ],
         'width':"900px",
         'pagination':50
     }
    }
]

unit = {
    'content_type':{
       'app_label':'units',
       'model':'baseunit'
    },
    'position':0,
    'constraints':unit_constraints,
    'children':[
        {'entity':derived},
    ]
}

parameter_constraints = [
    {'tableconstraint':{
         'displayed_in_navigator':False,
         'form':'helmholtz.editor.forms.measurements.ParameterForm',
         'in_header':[
             {'field':{'identifier':'id'}},
             {'field':{'identifier':'content_type'}},
             {'field':{'identifier':'label'}},
             {'field':{'identifier':'type'}},
             {'field':{'identifier':'unit'}},
             {'field':{'identifier':'is_constrained', 'verbose_name':'is constrained'}},
             
         ],
         'in_expansion':[
             {'field':{'identifier':'verbose_name'}},
             {'field':{'identifier':'pattern'}},
             {'field':{'identifier':'notes'}},
         ],
         'width':"750px",
         'pagination':50
     }
    }
]

parameter = {
    'content_type':{
       'app_label':'measurements',
       'model':'parameter'
    },
    'position':1,
    'constraints':parameter_constraints,
}


