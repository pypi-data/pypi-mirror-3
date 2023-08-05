import urllib, urllib2
from elementtree.ElementTree import XML


class Evri(object):
    url = 'http://api.evri.com/v1/media/entities'

    def __init__(self, api_key, relevance = 1.0):
        self.api_key = api_key
        self.relevance = relevance

    def analyze(self, url, text=None):
        if text:
            args = {'uri': url,
            'appId': self.api_key,
            'text': text}
        else:
            args = {'uri': url,
            'appId': self.api_key}
        args_enc = urllib.urlencode(args)
        output = urllib.urlopen(self.url, args_enc).read()
        results = []
        if output:
            dom = XML(output)
            aliases = []
            for alias in dom.findall('.//alias'):
                aliases.append(alias.text)
            for entity in dom.findall('.//entity'):
                name = entity.find('name')
                try:
                    if float(entity.attrib['score']) < self.relevance:
                        continue
                except KeyError:
                    pass
                if name != None:
                    if name.text in aliases:
                        continue
                cname = entity.find('canonicalName')
                if cname != None:
                    name = cname
                if name == None:
                    continue
                else:
                    if name.text in results:
                        continue
                results.append(name.text)
        return results
