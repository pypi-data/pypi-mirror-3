#encoding:utf-8
from helmholtz.core.populate import PopulateCommand
from helmholtz.editor.models import Node, View, Field, Constraint
from helmholtz.editor.management.commands.access_control_contraints import group, user, uac_entity, access_request
from helmholtz.editor.management.commands.trackers_constraints import connection#, email
from helmholtz.editor.management.commands.people_constraints import contact, skill, position_type, researcher, structure, supplier
from helmholtz.editor.management.commands.storage_constraints import protocol, mimetype, server, data_file
from helmholtz.editor.management.commands.measurements_constraints import parameter, unit
from helmholtz.editor.management.commands.neuralstructures_constraints import brain_region, cell_type
from helmholtz.editor.management.commands.species_constraints import species
from helmholtz.editor.management.commands.preparations_constraints import animal 
from helmholtz.editor.management.commands.chemistry_constraints import substance, product, solution, app_type 
from helmholtz.editor.management.commands.equipment_constraints import material, equipment_type, equipment, setup, device_configuration 
from helmholtz.editor.management.commands.analysis_constraints import pin_type, analysis_type
from helmholtz.editor.management.commands.signals_constraints import channel_type, recording_mode, channel, signal
from helmholtz.editor.management.commands.experiment_constraints import experiment
from helmholtz.editor.management.commands.stimulation_constraints import stimulus
from helmholtz.editor.management.commands.editor_constraints import view

Node.objects.all().delete()
Field.objects.all().delete()
Constraint.objects.all().delete()

#Administration View
view = {
    'name':'administration',
    'children':[
        #Editor section
#        {'section':{'position':0,
#         'title':'View System',
#         'children':[
#             {'entity':view},
#         ]
#        }
#        },
        #Access Control Section
        #Group, User, UnderAccessControlEntity, AccessRequest        
        {'section':{'position':1,
         'title':'Access Control',
         'children':[
             {'entity':group},
             {'entity':user},
             {'entity':uac_entity},
             {'entity':access_request},
             {'entity':connection},
             #{'entity':email},
         ]
        }
        },
        #Scientific Community Section
        {'section':{'position':2,
         'title':'Scientific Community',
         'children':[
             {'entity':contact},
             # {'entity':skill},
             {'entity':structure},
             {'section':{
                  'title':'Researcher Profiles',
                  'position':4,
                  'children':[
                       {'entity':position_type},
                       {'entity':researcher},
                  ]
              }
             },
             {'entity':supplier}
         ]
        }
        },
        #Data Storage Section
        {'section':{
             'position':3,
             'title':'Data Storage',
             'children':[
                 {'entity':protocol},
                 {'entity':mimetype},
                 {'entity':server},
                 {'entity':data_file},
             ]
        }
        },
        #units and parameters section
        {'section':{
             'position':4,
             'title':'Measurements',
             'children':[
                 {'entity':parameter},
                 {'entity':unit},
             ]
        }
        },
        {'section':{
             'position':5,
             'title':'Neural Structures',
             'children':[
                 {'entity':brain_region},
                 {'entity':cell_type},
             ]
        }
        },
        {'section':{
             'position':6,
             'title':'Preparation Information',
             'children':[
                 {'entity':species},
                 {'entity':animal},
             ]
        }
        },
        {'section':{
             'position':7,
             'title':'Chemistry',
             'children':[
                 {'entity':substance},
                 {'entity':product},
                 {'entity':app_type},
                 {'entity':solution},
             ]
        }
        },
        {'section':{
             'position':8,
             'title':'Equipment',
             'children':[
                 {'entity':material},
                 {'entity':equipment_type},
                 {'entity':equipment},
                 {'entity':setup},
                 {'entity':device_configuration},
             ]
        }
        },
#        {'section':{
#             'position':9,
#             'title':'Data Analysis',
#             'children':[
#                 {'entity':pin_type},
#                 {'entity':analysis_type},
#             ]
#        }
#        },
#        {'section':{
#             'position':10,
#             'title':'Signals',
#             'children':[
#                 {'entity':channel_type},
#                 {'entity':recording_mode},
#                 {'entity':channel},
#                 #{'entity':signal},
#             ]
#        }
#        },
#        {'section':{
#             'position':11,
#             'title':'Stimulation Database',
#             'children':[
#                 {'section':{
#                  'title':'Stimulation Details',
#                  'position':1,
#                  'children':[
#                      #  {'entity':screen},
#                      #  {'entity':screen_area},
#                      # {'entity':grid},
#                      # {'entity':bar},
#                  ]
#                  }
#                 },
#                 {'entity':stimulus},
#             ]
#        }
#        },
#        {'section':{
#             'position':12,
#             'title':'Experiments',
#             'children':[
#                 {'entity':experiment},
#             ]
#        }
#        }
    ]
}

class Command(PopulateCommand):
    help = "populate editor administration view"
    priority = 0
    data = [
        {'class':View, 'objects':[view]}    
    ]
