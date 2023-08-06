# encoding: utf-8
from helmholtz.analysis.tools.authentication import authenticate
from helmholtz.analysis.tools.factories.django.components import ComponentFactory as RegisteredComponentFactory
from helmholtz.analysis.tools.factories.django.analyses import AnalysisFactory as RegisteredAnalysisFactory
from helmholtz.analysis.tools.factories.xml.components import ComponentFactory as XMLComponentFactory
from helmholtz.analysis.tools.factories.xml.analyses import AnalysisFactory as XMLAnalysisFactory
from helmholtz.analysis.tools.managers.django import DjangoManager as Manager

comp = None
an = None

def launch_analysis(model, configuration) :    
    compfactory = comp(model)
    anfactory = an(configuration)    
    pipeline = compfactory.create_component()
    analysis = anfactory.create_analysis(pipeline)
    register, snapshot = analysis.launch()
    if register :
        print register
        if snapshot :
            print snapshot

if __name__ == "__main__" :
    
    #authentication is required to be able to store data into a database
    #if the authentication is not done, is it anyway possible to launch the computation
    #if register=False and snapshot=False
    authenticate('thierry', 'brizzi2007', Manager())
    
    #1:When model and configuration are stored into XML files 
    #model = "file:///home/thierry/Benchmarks_Project/benchmarks/contrast_response_component_chisquare.xml"
    #configuration = "file:///home/thierry/Benchmarks_Project/benchmarks/contrast_response_analysis_db.xml"
    #comp = XMLComponentFactory
    #an = XMLAnalysisFactory
    
    #2:When model and configuration are stored into database
    #model = "ContrastResponsePipeline"
    #configuration = "ContrastResponseTestDB"
    #comp = RegisteredComponentFactory
    #an = RegisteredAnalysisFactory
    
    #Start the analysis from the model and configuration
    launch_analysis(model, configuration)
    print "Done !!!"
