#encoding:utf-8
from copy import deepcopy

#screen = {
#    'content_type':{
#       'app_label':'visualstimulation',
#       'model':'screenphotometry'
#    },
#    'position':1,
#    'constraints':[
#        {
#         'tableconstraint':{
#             'form':'helmholtz.editor.forms.stimuli.ScreenPhotometryForm',
#             'displayed_in_navigator':False,
#             'shunt':True,
#             'in_header':[
#                 {'field':{'identifier':'id'}},
#                 {'field':{'identifier':'luminance_high'}},
#                 {'field':{'identifier':'luminance_low'}},
#                 {'field':{'identifier':'luminance_background'}},
#                 {'field':{'identifier':'gray_levels'}},
#             ],
#             'width':"700px",
#             'pagination':50
#         }
#        }
#    ]
#}

#screen_area = {
#    'content_type':{
#       'app_label':'visualstimulation',
#       'model':'screenarea'
#    },
#    'position':2,
#    'constraints':[
#        {
#         'tableconstraint':{
#             'form':'helmholtz.editor.forms.stimuli.ScreenAreaForm',
#             'displayed_in_navigator':False,
#             'shunt':True,
#             'in_header':[
#                 {'field':{'identifier':'id'}},
#                 {'field':{'identifier':'position_x'}},
#                 {'field':{'identifier':'position_y'}},
#                 {'field':{'identifier':'width'}},
#                 {'field':{'identifier':'length'}},
#                 {'field':{'identifier':'orientation'}},
#             ],
#             'width':"700px",
#             'pagination':50
#         }
#        }
#    ]
#}

#bar = {
#    'content_type':{
#       'app_label':'visualstimulation',
#       'model':'bar'
#    },
#    'position':3,
#    'constraints':[
#        {
#         'tableconstraint':{
#             'form':'helmholtz.editor.forms.stimuli.BarForm',
#             'displayed_in_navigator':False,
#             'shunt':True,
#             'in_header':[
#                 {'field':{'identifier':'id'}},
#                 {'field':{'identifier':'excursion'}},
#                 {'field':{'identifier':'speed'}},
#                 {'field':{'identifier':'length'}},
#                 {'field':{'identifier':'width'}}
#             ],
#             'width':"700px",
#             'pagination':50
#         }
#        } 
#    ]
#}

#grid = {
#    'content_type':{
#       'app_label':'vision',
#       'model':'grid'
#    },
#    'position':4,
#    'constraints':[
#        {
#         'tableconstraint':{
#             'form':'helmholtz.editor.forms.stimuli.GridForm',
#             'displayed_in_navigator':False,
#             'shunt':True,
#             'in_header':[
#                 {'field':{'identifier':'id'}},
#                 {'field':{'identifier':'n_div_x'}},
#                 {'field':{'identifier':'n_div_y'}},
#                 {'field':{'identifier':'expansion'}},
#                 {'field':{'identifier':'scotoma'}},
#                 {'field':{'identifier':'type'}}
#             ],
#             'width':"700px",
#             'pagination':50
#         }
#        }
#    ]
#}

#stim_screen = {
#    'content_type':{
#       'app_label':'visualstimulation',
#       'model':'screenphotometry'
#    },
#    'position':1,
#    'constraints':[
#        {
#         'form':'helmholtz.editor.forms.stimuli.ScreenPhotometryForm',
#         'in_expansion':[
#             {'field':{'identifier':'id'}},
#             {'field':{'identifier':'luminance_high'}},
#             {'field':{'identifier':'luminance_low'}},
#             {'field':{'identifier':'luminance_background'}},
#             {'field':{'identifier':'gray_levels'}},
#         ]
#        }
#    ]
#}

#stim_screen_area = {
#    'content_type':{
#       'app_label':'visualstimulation',
#       'model':'screenarea'
#    },
#    'position':1,
#    'constraints':[
#        {
#         'form':'helmholtz.editor.forms.stimuli.ScreenAreaForm',
#         'in_expansion':[
#             {'field':{'identifier':'id'}},
#             {'field':{'identifier':'position_x'}},
#             {'field':{'identifier':'position_y'}},
#             {'field':{'identifier':'width'}},
#             {'field':{'identifier':'length'}},
#             {'field':{'identifier':'orientation'}},
#         ]
#        }
#    ]
#}

#stim_bar = {
#    'content_type':{
#       'app_label':'visualstimulation',
#       'model':'bar'
#    },
#    'position':1,
#    'constraints':[
#        {
#         'form':'helmholtz.editor.forms.stimuli.BarForm',
#         'in_expansion':[
#             {'field':{'identifier':'id'}},
#             {'field':{'identifier':'excursion'}},
#             {'field':{'identifier':'speed'}},
#             {'field':{'identifier':'length'}},
#             {'field':{'identifier':'width'}}
#         ]
#        }
#    ]
#}

#stim_grid = {
#    'content_type':{
#       'app_label':'vision',
#       'model':'grid'
#    },
#    'position':1,
#    'constraints':[
#        {
#         'form':'helmholtz.editor.forms.stimuli.GridForm',
#         'in_expansion':[
#             {'field':{'identifier':'id'}},
#             {'field':{'identifier':'n_div_x'}},
#             {'field':{'identifier':'n_div_y'}},
#             {'field':{'identifier':'expansion'}},
#             {'field':{'identifier':'scotoma'}},
#             {'field':{'identifier':'type'}}
#         ]
#        }
#    ]
#}

flashbar_constraints = {
    'tableconstraint':{
        'displayed_in_navigator':False,
        'shunt':False,
        'form':'helmholtz.editor.forms.stimuli.FlashBarForm',
        'in_header':[
            {'field':{'identifier':'id'}},
            {'field':{'identifier':'label'}},
            {'field':{'identifier':'stimulus_generator'}},
            {'field':{'identifier':'driven_eye'}},
            {'field':{'identifier':'viewing_distance'}},
            {'field':{'identifier':'number_of_repetitions'}},
            {'field':{'identifier':'title'}},
            {'field':{
                'force':True,
                'identifier':'stimulation_area',
                'subfields':[
                    {'subfield':{'identifier':'rf_x', 'verbose_name':'X'}},
                    {'subfield':{'identifier':'rf_y', 'verbose_name':'Y'}},
                    {'subfield':{'identifier':'rf_w', 'verbose_name':'W'}},
                    {'subfield':{'identifier':'rf_l', 'verbose_name':'L'}},
                    {'subfield':{'identifier':'rf_t', 'verbose_name':'&theta;'}},
                ]
                }
            },
            {'field':{
                'force':True,
                'identifier':'bar',
                'subfields':[
                    {'subfield':{'identifier':'excursion', 'verbose_name':'excursion'}},
                    {'subfield':{'identifier':'dt_on'}},
                    {'subfield':{'identifier':'number_of_orientations', 'verbose_name':'N<sub>&theta;</sub>'}},
                    {'subfield':{'identifier':'orientation_min', 'verbose_name':'&theta;<sub>min</sub>'}},
                    {'subfield':{'identifier':'orientation_max', 'verbose_name':'&theta;<sub>max</sub>'}},
                    {'subfield':{'identifier':'orientation_step', 'verbose_name':'&theta;<sub>step</sub>'}},
                ]
                }
            }
        ],
        'in_expansion':[
            # {'field':{'identifier':'stimulation_area'}},
            # {'field':{'identifier':'orientations'}},
        ],
        'width':"1250px",
        'pagination':50
    }
}

flashbar = {
    'content_type':{
       'app_label':'vision',
       'model':'flashbar'
    },
    'position':3,
    'constraints':[
        flashbar_constraints
    ],
    'children':[
        # {'entity':deepcopy(stim_screen_area)},
    ]
}

movingbar_constraints = {
    'tableconstraint':{
        'displayed_in_navigator':False,
        'shunt':False,
        'form':'helmholtz.editor.forms.stimuli.MovingBarForm',
        'in_header':[
            {'field':{'identifier':'id'}},
            {'field':{'identifier':'label'}},
            {'field':{'identifier':'stimulus_generator'}},
            {'field':{'identifier':'driven_eye'}},
            {'field':{'identifier':'viewing_distance'}},
            {'field':{'identifier':'number_of_repetitions'}},
            {'field':{'identifier':'title'}},
            {'field':{
                'force':True,
                'identifier':'stimulation_area',
                'subfields':[
                    {'subfield':{'identifier':'rf_x', 'verbose_name':'Pos<sub>X</sub>'}},
                    {'subfield':{'identifier':'rf_y', 'verbose_name':'Pos<sub>Y</sub>'}},
                    {'subfield':{'identifier':'rf_w', 'verbose_name':'W'}},
                    {'subfield':{'identifier':'rf_l', 'verbose_name':'L'}},
                    {'subfield':{'identifier':'rf_t', 'verbose_name':'&theta;'}},
                ]
                }
            },
            {'field':{
                'force':True,
                'identifier':'bar',
                'subfields':[
                    {'subfield':{'identifier':'width', 'verbose_name':'W'}},
                    {'subfield':{'identifier':'length', 'verbose_name':'L'}},
                    {'subfield':{'identifier':'excursion', 'verbose_name':'excursion'}},
                    {'subfield':{'identifier':'speed', 'verbose_name':'speed'}},
                    {'subfield':{'identifier':'get_dt_on', 'verbose_name':'dt on'}},
                    {'subfield':{'identifier':'number_of_orientations', 'verbose_name':'N<sub>&theta;</sub>'}},
                    {'subfield':{'identifier':'orientation_min', 'verbose_name':'&theta;<sub>min</sub>'}},
                    {'subfield':{'identifier':'orientation_max', 'verbose_name':'&theta;<sub>max</sub>'}},
                    {'subfield':{'identifier':'orientation_step', 'verbose_name':'&theta;<sub>step</sub>'}},
                ]
                }
            }
        ],
        'in_expansion':[
            # {'field':{'identifier':'stimulation_area'}},
            # {'field':{'identifier':'bar'}},
            {'field':{'identifier':'orientations'}},
        ],
        'width':"1250px",
        'pagination':50
    }
}

movingbar = {
    'content_type':{
       'app_label':'vision',
       'model':'movingbar'
    },
    'position':2,
    'constraints':[
        movingbar_constraints
    ],
    'children':[
        # {'entity':deepcopy(stim_screen_area)},
        # {'entity':deepcopy(stim_bar)},
    ]
}

densenoise_constraints = {
    'tableconstraint':{
        'displayed_in_navigator':False,
        'shunt':False,
        'form':'helmholtz.editor.forms.stimuli.DenseNoiseForm',
        'in_header':[
            {'field':{'identifier':'id'}},
            {'field':{'identifier':'label'}},
            {'field':{'identifier':'stimulus_generator'}},
            {'field':{'identifier':'driven_eye'}},
            {'field':{'identifier':'viewing_distance'}},
            {'field':{'identifier':'type'}},
            {'field':{'identifier':'number_of_sequences'}},
            {'field':{'identifier':'stimulus_duration'}},
            {'field':{'identifier':'pretrigger_duration'}},
            {'field':{'identifier':'seed'}},
            {'field':{'identifier':'dt_on'}},
            {'field':{'identifier':'dt_off'}},
            {'field':{'identifier':'title'}},
            {'field':{
                'force':True,
                'identifier':'screen',
                'subfields':[
                    {'subfield':{'identifier':'gray_levels', 'verbose_name':'N<sub>grey</sub>'}},
                    {'subfield':{'identifier':'luminance_high', 'verbose_name':'L<sub>h</sub>'}},
                    {'subfield':{'identifier':'luminance_low', 'verbose_name':'L<sub>l</sub>'}},
                    {'subfield':{'identifier':'luminance_background', 'verbose_name':'L<sub>b</sub>'}},
                ]
                }
            },
            {'field':{
                'force':True,
                'identifier':'stimulation_area',
                'subfields':[
                    {'subfield':{'identifier':'rf_x', 'verbose_name':'Pos<sub>X</sub>'}},
                    {'subfield':{'identifier':'rf_y', 'verbose_name':'Pos<sub>Y</sub>'}},
                    {'subfield':{'identifier':'rf_w', 'verbose_name':'W'}},
                    {'subfield':{'identifier':'rf_l', 'verbose_name':'L'}},
                    {'subfield':{'identifier':'rf_t', 'verbose_name':'&theta;'}},
                ]
                }
            },
            {'field':{
                'force':True,
                'identifier':'grid',
                'subfields':[
                    {'subfield':{'identifier':'n_div_x', 'verbose_name':'Div<sub>X</sub>'}},
                    {'subfield':{'identifier':'n_div_y', 'verbose_name':'Div<sub>Y</sub>'}},
                    {'subfield':{'identifier':'expansion', 'verbose_name':'expansion'}},
                    {'subfield':{'identifier':'scotoma', 'verbose_name':'scotoma'}},
                ]
                }
            }
        ],
        'in_expansion':[
            # {'field':{'identifier':'screen'}},
            # {'field':{'identifier':'stimulation_area'}},
            # {'field':{'identifier':'grid'}},
        ],
        'width':"1250px",
        'pagination':50
    }
}

densenoise = {
    'content_type':{
       'app_label':'vision',
       'model':'densenoise'
    },
    'position':4,
    'constraints':[
        densenoise_constraints
    ],
    'children':[
        # {'entity':deepcopy(stim_screen)},
        # {'entity':deepcopy(stim_screen_area)},
        # {'entity':deepcopy(stim_grid)},
    ]
    
}

sparsenoise_constraints = {
    'tableconstraint':{
        'displayed_in_navigator':False,
        'shunt':False,
        'form':'helmholtz.editor.forms.stimuli.RevCorForm',
        'in_header':[
            {'field':{'identifier':'id'}},
            {'field':{'identifier':'label'}},
            {'field':{'identifier':'stimulus_generator'}},
            {'field':{'identifier':'driven_eye'}},
            {'field':{'identifier':'viewing_distance'}},
            {'field':{'identifier':'seed'}},
            {'field':{'identifier':'dt_on'}},
            {'field':{'identifier':'dt_off'}},
            {'field':{'identifier':'title'}},
            {'field':{
                'force':True,
                'identifier':'screen',
                'subfields':[
                    {'subfield':{'identifier':'gray_levels', 'verbose_name':'N<sub>grey</sub>'}},
                    {'subfield':{'identifier':'luminance_high', 'verbose_name':'L<sub>h</sub>'}},
                    {'subfield':{'identifier':'luminance_low', 'verbose_name':'L<sub>l</sub>'}},
                    {'subfield':{'identifier':'luminance_background', 'verbose_name':'L<sub>b</sub>'}},
                ]
                }
            },
            {'field':{
                'force':True,
                'identifier':'stimulation_area',
                'subfields':[
                    {'subfield':{'identifier':'rf_x', 'verbose_name':'X'}},
                    {'subfield':{'identifier':'rf_y', 'verbose_name':'Y'}},
                    {'subfield':{'identifier':'rf_w', 'verbose_name':'W'}},
                    {'subfield':{'identifier':'rf_l', 'verbose_name':'L'}},
                    {'subfield':{'identifier':'rf_t', 'verbose_name':'&theta;'}},
                ]
                }
            },
            {'field':{
                'force':True,
                'identifier':'grid',
                'subfields':[
                    {'subfield':{'identifier':'n_div_x', 'verbose_name':'Div<sub>X</sub>'}},
                    {'subfield':{'identifier':'n_div_y', 'verbose_name':'Div<sub>Y</sub>'}},
                    {'subfield':{'identifier':'expansion', 'verbose_name':'expansion'}},
                    {'subfield':{'identifier':'scotoma', 'verbose_name':'scotoma'}},
                ]
               }
            }
        ],
        'in_expansion':[
            # {'field':{'identifier':'screen'}},
            # {'field':{'identifier':'stimulation_area'}},
            # {'field':{'identifier':'grid'}},
        ],
        'width':"1250px",
        'pagination':50
    }
}

sparsenoise = {
    'content_type':{
       'app_label':'vision',
       'model':'sparsenoise'
    },
    'position':1,
    'constraints':[
        sparsenoise_constraints
    ],
    'children':[
        # {'entity':deepcopy(stim_screen)},
        # {'entity':deepcopy(stim_screen_area)},
        # {'entity':deepcopy(stim_grid)},
    ]
}

stimulus_constraints = {
        #'form':'helmholtz.editor.forms.stimuli.StimulusForm',
        'display_subclasses':True,
        'excluded_subclasses':[
            {'app_label':'visualstimulation', 'model':'visualstimulus'},
            {'app_label':'stimulation', 'model':'nullstimulus'},
            {'app_label':'vision', 'model':'centersurroundstimulus'},
            {'app_label':'vision', 'model':'sparsenoisesurround'},
            {'app_label':'vision', 'model':'densenoisesurround'},
            {'app_label':'vision', 'model':'gratingsurround'},
            {'app_label':'vision', 'model':'gratingcenter'},
            {'app_label':'vision', 'model':'naturenoisenetwork'},
            {'app_label':'electricalstimulation', 'model':'electricalstimulus'},
            {'app_label':'vision', 'model':'gaby'},
            {'app_label':'vision', 'model':'gabornoise'},
            {'app_label':'vision', 'model':'spatialfrequencyandphase'},
            {'app_label':'vision', 'model':'temporalfrequency'},
            {'app_label':'vision', 'model':'evoquedresponse'},
            {'app_label':'vision', 'model':'thetaburst'},
            {'app_label':'vision', 'model':'orientation'},
            {'app_label':'vision', 'model':'saccadeflik'},
            {'app_label':'vision', 'model':'pairinggabor'},
            {'app_label':'vision', 'model':'pairingposition'},
            {'app_label':'vision', 'model':'hybrid'},
            {'app_label':'vision', 'model':'tuning'},
            {'app_label':'vision', 'model':'ivcurve'},
            {'app_label':'vision', 'model':'lgnstimulation'},
            {'app_label':'vision', 'model':'currentstepstimulus'},
            {'app_label':'vision', 'model':'saccademove'},
            {'app_label':'vision', 'model':'hexagabor'},
        ]
}

stimulus = {
    'content_type':{
       'app_label':'stimulation',
       'model':'stimulus'
    },
    'position':2,
    'constraints':[
        stimulus_constraints
    ],
    'children':[
        {'entity':sparsenoise},
        {'entity':densenoise},
        {'entity':movingbar},
        {'entity':flashbar}
    ]
}
