connection_constraints = [
    {'tableconstraint':{
         'displayed_in_navigator':False,
         'shunt':True,
         'actions':[
             {'name':'N'}
         ],
         'in_header':[
             {'field':{'identifier':'id'}},
             {'field':{'identifier':'date'}},
             {'field':{'identifier':'user'}}    
         ],
         'width':"500px",
         'pagination':100
     }
    }
]

connection = {
    'content_type':{
       'app_label':'trackers',
       'model':'connectiontracker'
    },
    'position':6,
    'constraints':connection_constraints,
}
