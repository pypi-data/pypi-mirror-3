substance_constraints = [
    {
     'displayed_in_navigator':True,
     'shunt':True,
     'form':'helmholtz.editor.forms.chemistry.SubstanceForm',
    }
]

substance = {
    'content_type':{
       'app_label':'chemistry',
       'model':'substance'
    },
    'position':1,
    'constraints':substance_constraints,
}

app_type = {
    'content_type':{
       'app_label':'chemistry',
       'model':'applicationtype'
    },
    'position':4,
    'constraints':[{
        'displayed_in_navigator':True,
        'shunt':True,
        'form':'helmholtz.editor.forms.chemistry.ApplicationTypeForm'
    }]
}

product_constraints = [
    {'tableconstraint':{
         'displayed_in_navigator':False,
         'shunt':True,
         'form':'helmholtz.editor.forms.chemistry.ProductForm',
         'in_header':[
             {'field':{'identifier':'id'}},
             {'field':{'identifier':'name'}},
             {'field':{'identifier':'substance'}},
             {'field':{'identifier':'supplier'}},
             {'field':{'identifier':'catalog_ref'}}
         ],
         'in_expansion':[
         
         ],
         'width':"1100px",
         'pagination':50
     }
    }
]

product = {
    'content_type':{
       'app_label':'chemistry',
       'model':'product'
    },
    'position':2,
    'constraints':product_constraints,
}

solution_quantity_of_substance_constraints = [
    {'tableconstraint':{
         'actions':[
             {'name':'A'},
             {'name':'M'},
             {'name':'D'},
         ],
         'in_header':[
             {'field':{'identifier':'id'}},
             {'field':{'identifier':'chemical_product'}},
             {'field':{'identifier':'concentration'}},
         ],
         'displayed_in_navigator':False,
         'shunt':True,
         'form':'helmholtz.editor.forms.chemistry.QuantityOfSubstanceForm',
         'width':'650px',
         'pagination':25
    }
   }  
]

solution_quantity_of_substance = {
    'content_type':{
       'app_label':'chemistry',
       'model':'quantityofsubstance'
    },
    'position':1,
    'constraints':solution_quantity_of_substance_constraints,
}

application_types = {
    'content_type':{
       'app_label':'chemistry',
       'model':'applicationtype'
    },
    'position':0,
    'constraints':[{
        'displayed_in_navigator':False,
        'shunt':True,
        'form':'helmholtz.editor.forms.chemistry.ApplicationTypeForm',
    }]
}

solution_constraints = [
    {'tableconstraint':{
         'displayed_in_navigator':False,
         'form':'helmholtz.editor.forms.chemistry.SolutionForm',
         'in_expansion':[
             {'field':{'identifier':'applications'}},
             {'field':{'identifier':'quantityofsubstance_set'}},
         ],
         'in_header':[
             {'field':{'identifier':'label'}},
             {'field':{'verbose_name':'applications', 'identifier':'applications.count'}},
             {'field':{'verbose_name':'components', 'identifier':'quantityofsubstance_set.count'}},
         ],
         'width':"750px",
         'pagination':50
     }
    }
]

solution = {
    'content_type':{
       'app_label':'chemistry',
       'model':'solution'
    },
    'position':3,
    'constraints':solution_constraints,
    'children':[
        {'entity':application_types},
        {'entity':solution_quantity_of_substance},
    ]
}
