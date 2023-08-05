# generate Subjects

import yql
from calais import Calais
from silcc import Silcc
from tagthenet import TagTheNet
from AlchemyAPI import AlchemyAPI
from zemanta import Zemanta
from amplify import Amplify
from evri import Evri

from zope.component import getUtility
from plone.registry.interfaces import IRegistry
from collective.taghelper.interfaces import ITagHelperSettingsSchema

from elementtree.ElementTree import XML




PREFERRED_ENTITIES = ['City', 'Continent', 'Country', 'MedicalCondition',
    'MedicalTreatment', 'NaturalFeature', 'Organization', 'ProvinceOrState',
    'Region', 'IndustryTerm']
PREFERRED_FACTS = ['EnvironmentalIssue', 'ManMadeDisaster', 'NaturalDisaster']

def get_evri_subjects(url, text=None):
    registry = getUtility(IRegistry)
    settings = registry.forInterface(ITagHelperSettingsSchema)
    api_key = settings.evri_api_key
    relevance = settings.evri_relevance
    results = []
    if api_key:
        evriObj = Evri(api_key, relevance)
        results = evriObj.analyze(url, text)
    return results


def get_amplify_subjects(text):
    registry = getUtility(IRegistry)
    settings = registry.forInterface(ITagHelperSettingsSchema)
    api_key = settings.openamplify_api_key
    results = []
    if api_key:
        amplifyObj = Amplify(api_key)
        results = amplifyObj.amplify(text)
    return results

def get_amplify_subjects_remote(url):
    registry = getUtility(IRegistry)
    settings = registry.forInterface(ITagHelperSettingsSchema)
    api_key = settings.amplify_api_key
    results = []
    a_url = 'sourceURL=' + url
    if api_key:
        amplifyObj = Amplify(api_key)
        results = amplifyObj.amplify(a_url)
    return results


def get_zemanta_subjects(text, title=''):
    registry = getUtility(IRegistry)
    settings = registry.forInterface(ITagHelperSettingsSchema)
    api_key = settings.zemanta_api_key
    relevance = settings.zemanta_relevance
    results = []
    if api_key:
        zemantaObj = Zemanta(api_key, relevance)
        results = zemantaObj.analyze(text, title)
    return results


def _list_alchemy_results(xml,relevance):
    dom = XML(xml)
    results = []
    if dom.find('status').text == 'OK':
        for concept in dom.findall('.//concept'):
            if float(concept.find('relevance').text) > relevance:
                results.append(concept.find('text').text)
        for kw in dom.findall('.//keyword'):
            if float(kw.find('relevance').text) > relevance:
                results.append(kw.find('text').text)
    return results


def get_alchemy_subjects(text):
    registry = getUtility(IRegistry)
    settings = registry.forInterface(ITagHelperSettingsSchema)
    api_key = settings.alchemy_api_key
    relevance = settings.alchemy_relevance
    results = []
    if api_key:
        alchemyObj = AlchemyAPI()
        alchemyObj.setAPIKey(api_key)
        try:
            result = alchemyObj.TextGetRankedConcepts(text)
            results += _list_alchemy_results(result, relevance)
            #result = alchemyObj.TextGetRankedKeywords(text)
            #results += _list_alchemy_results(result)
            #results = list(set(results))
            return results
        except:
            return results
    else:
        return results

def get_alchemy_subjects_remote(url):
    registry = getUtility(IRegistry)
    settings = registry.forInterface(ITagHelperSettingsSchema)
    api_key = settings.alchemy_api_key
    if api_key:
        alchemyObj = AlchemyAPI()
        alchemyObj.setAPIKey(api_key)
        try:
            result = alchemyObj.URLGetRankedConcepts(url)
            results += _list_alchemy_results(result)
            #result = alchemyObj.URLGetRankedKeywords(url)
            #results += _list_alchemy_results(result)
            #results = list(set(results))
            return results
        except:
            return results
    else:
        return results

def get_yql_subjects_remote(url):
    registry = getUtility(IRegistry)
    settings = registry.forInterface(ITagHelperSettingsSchema)
    api_key = settings.yahoo_api_key
    if api_key:
        y = yql.Public(api_key)
        query = '''select * from search.termextract where context in (
                select content from html where url="%s"
                )''' % url
        try:
            result = y.execute(query)
        except:
            return []
        return result.rows
    else:
        return []


def get_yql_subjects(text):
    registry = getUtility(IRegistry)
    settings = registry.forInterface(ITagHelperSettingsSchema)
    api_key = settings.yahoo_api_key
    if api_key:
        y = yql.Public(api_key)
        query = '''select * from search.termextract where context ="%s"
                ''' % text.replace('"',"'")
        try:
            result = y.execute(query)
        except:
            return []
        return result.rows
    else:
        return []

def get_ttn_subjects(text):
    ttn = TagTheNet()
    return ttn.analyze(text)

def get_ttn_subjects_remote(url):
    ttn = TagTheNet()
    return ttn.analyze_url(url)


def get_silcc_subjects(text):
    registry = getUtility(IRegistry)
    settings = registry.forInterface(ITagHelperSettingsSchema)
    api_key = settings.silcc_api_key
    if api_key == None:
        api_key=''
    url  = settings.silcc_url
    silcc = Silcc(api_key, url)
    try:
        return silcc.execute(text)
    except:
        return []

def get_calais_subjects(text, uid):
    registry = getUtility(IRegistry)
    settings = registry.forInterface(ITagHelperSettingsSchema)
    api_key = settings.calais_api_key
    relevance = settings.calais_relevance
    subjects=[]
    if api_key:
        calais = Calais(api_key)
        try:
            result = calais.analyze(text, external_id = uid)
        except:
            return []
        #if hasattr( result, 'entities'):
        #    for entity in result.entities:
        #        if entity['_type'] in PREFERRED_ENTITIES:
        #            subjects.append(entity['name'])
        if hasattr( result, 'socialTag'):
            for tag in result.socialTag:
                if float(tag['importance']) > relevance:
                    subjects.append(tag['name'])
        #if hasattr( result, 'relations'):
        #    for fact in result.relations:
        #        if fact['_type'] in PREFERRED_FACTS:
        #            ft = fact.get(fact['_type'].lower())
        #            if ft:
        #                subjects.append(ft)
    return subjects
