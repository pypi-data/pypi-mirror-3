animal_constraints = [
    {'tableconstraint':{
         'shunt':True,
         'actions':[
             {'name':'A'},
             {'name':'M'},
             {'name':'D'},
         ],
         'in_header':[
             {'field':{'identifier':'id'}},
             {'field':{'identifier':'identifier'}},
             {'field':{'identifier':'strain'}},
             {'field':{'identifier':'sex'}},
             {'field':{'identifier':'supplier'}},
             {'field':{'identifier':'birth'}},
             {'field':{'identifier':'sacrifice'}},
             {'field':{'verbose_name':'age (weeks)', 'identifier':'age'}},
         ],
         'displayed_in_navigator':False,
         'form':'helmholtz.editor.forms.preparations.AnimalForm',
         'width':'800px',
         'pagination':25
    }
   }  
]

animal = {
    'content_type':{
       'app_label':'preparations',
       'model':'animal'
    },
    'position':2,
    'constraints':animal_constraints,
}
