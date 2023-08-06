#encoding:utf-8
#data coming from http://www.itis.gov/downloads/
from django.conf import settings
from helmholtz.core.populate import PopulateCommand
from helmholtz.species.models import Species

CATALOG_OF_LIFE_TREE = "http://www.catalogueoflife.org/annual-checklist/2010/browse/tree/id/"
year = 2010

def get_name_code(traductions, id):
    if id in traductions and 'code' in traductions[id] :
        return traductions[id]['code'] 
    else :
        return None

def get_english_name(traductions, id):
    if id in traductions and 'English' in traductions[id] :
        return traductions[id]['English'] 
    else :
        return None

#get traductions of latin names
data = open('H:/Thierry/Helmholtz_Refactoring/helmholtz/species/management/commands/common_names.csv')
rows = [k.split(';') for k in data.xreadlines()]
traductions = dict()
for row in rows[1:] :
    id = int(row[0][1:-1])
    traduction = row[2][1:-1]
    language = row[3][1:-1]
    code = row[1][1:-1]
    if not id in traductions :
        traductions[id] = dict()
    traductions[id][language] = traduction
    traductions[id]['code'] = code

#get id for each following taxon
species = list()
data = open('H:/Thierry/Helmholtz_Refactoring/helmholtz/species/management/commands/taxa.csv')
rows = [k.split(';') for k in data.xreadlines()]
for row in rows[1:] :
    id = int(row[0][1:-1])
    lsid = row[1][1:-1]
    name = row[2][1:-1]
    code = get_name_code(traductions, id)
    #taxon = row[4][1:-1]
    eng_name = get_english_name(traductions, int(row[0][1:-1]))
    url = CATALOG_OF_LIFE_TREE + id
    item = {'id':id,
            'lsid':lsid,
            'scientific_name':name,
#            'taxon':{
#                'name':taxon
#            },
            'codename':code,
            'english_name':eng_name,
            'url':url
            }
#    p_id = int(row[6][1:-1]) 
#    if p_id :
#        item['parent'] = dict()
#        item['parent']['id'] = p_id
    species.append(item)
    
class Command(PopulateCommand):
    help = "populate species"
    priority = 1
    data = [
        {'class':Species, 'objects':species}    
    ]
