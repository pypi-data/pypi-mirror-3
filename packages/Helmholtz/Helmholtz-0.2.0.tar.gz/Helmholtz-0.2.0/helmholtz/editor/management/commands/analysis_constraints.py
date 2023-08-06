pin_type_constraints = [
    {'tableconstraint':{
         'displayed_in_navigator':False,
         'shunt':False,
         'form':'helmholtz.editor.forms.analysis.PinTypeForm',
         'excluded_fields':[
             {'name':'pin_set'},
         ],
         'properties':[
             {'name':'analyses', 'notation':'count_analyses'},
         ],
         'in_expansion':[
             {'name':'description'}
         ],
         'out_expansion':[
             {'name':'content_type'}
         ],
         'width':"600px",
         'pagination':50
     }
    }
]

pin_type = {
    'content_type':{
       'app_label':'analysis',
       'model':'pintype'
    },
    'position':1,
    'constraints':pin_type_constraints,
}

analysis_pin_type_constraints = [
    {'tableconstraint':{
         'displayed_in_navigator':False,
         'shunt':False,
         'form':'helmholtz.editor.forms.analysis.PinTypeFromAnalysisForm',
         'excluded_fields':[
             {'name':'pin_set'},
         ],
         'properties':[
             {'name':'analyses', 'notation':'count_analyses'},
         ],
         'in_expansion':[
             {'name':'description'}
         ],
         'out_expansion':[
             {'name':'content_type'}
         ],
         'width':"600px",
         'pagination':50
     }
    }
]

analysis_pin_type = {
    'content_type':{
       'app_label':'analysis',
       'model':'pintype'
    },
    'position':1,
    'constraints':analysis_pin_type_constraints,
}

analysis_type_constraints = [
    {'tableconstraint':{
         'displayed_in_navigator':False,
         'form':'helmholtz.editor.forms.analysis.AnalysisTypeForm',
         'excluded_fields':[
             {'name':'analysis_set'},
         ],
         'properties':[
             {'name':'analyses', 'notation':'analysis_set.count'},
             {'name':'pins', 'notation':'count_pins'},
             {'name':'inputs', 'notation':'inputs.count'},
             {'name':'parameters', 'notation':'parameters.count'},
             {'name':'outputs', 'notation':'outputs.count'},
         ],
         'in_expansion':[
             {'name':'description'}    
         ],
         'width':"900px",
         'pagination':50
     }
    }
]

analysis_type = {
    'content_type':{
       'app_label':'analysis',
       'model':'analysistype'
    },
    'position':2,
    'constraints':analysis_type_constraints,
    'children':[
        {'entity':analysis_pin_type},
    ]
}
