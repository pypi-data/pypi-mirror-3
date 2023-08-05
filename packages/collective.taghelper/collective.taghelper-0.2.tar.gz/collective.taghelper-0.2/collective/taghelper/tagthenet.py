#call TagThe.net webservices
import urllib, urllib2
try:
    import simplejson as json
except ImportError:
    import json

class TagTheNet(object):
    url = 'http://tagthe.net/api/'

    def __init__(self):
        pass

    def _analyze(self, params):
        self.language = []
        self.topics = []
        self.location = []
        results = json.load(urllib2.urlopen(self.url, data=params))
        result = results.get('memes',[])
        for meme in result:
            dim = meme.get('dimensions')
            if dim:
                self.language = self.language + dim.get('language', [])
                self.topics = self.topics + dim.get('topic', [])
                self.location = self.location + dim.get('location', [])
        return self.topics

    def analyze_url(self, url):
        '''
        http://tagthe.net/api/?url=http://www.knallgrau.at/en&view=json
        '''
        keywords = []
        try:
            params = urllib.urlencode({'url':url, 'view':'json'})
            keywords = self._analyze(params)
        except:
            pass
        return keywords

    def analyze(self, text):
        '''
        http://tagthe.net/api/?text=Hello%20World!
        '''
        keywords = []
        try:
            params = urllib.urlencode({'text':text, 'view':'json'})
            keywords = self._analyze(params)
        except:
            pass
        return keywords
