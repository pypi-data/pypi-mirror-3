import urllib, urllib2
try:
    import simplejson as json
except ImportError:
    import json

class Amplify(object):

    url = "http://portaltnx20.openamplify.com/AmplifyWeb_v20/AmplifyThis"

    def __init__(self, api_key):
        self.api_key = api_key


    def amplify(self, text, analysis='topics'):
        """
        Send a request to the openamplify server
        Arguments:
          analysis - 'all','topics','actions','demographics','styles'
          output_format - 'xml','json','dart'
        """

        post_parameters = {
            'inputtext': text,
            'apiKey': self.api_key,
            'outputformat':'json',
            'analysis':analysis,
        }
        args_enc = urllib.urlencode(post_parameters)
        try:
            response = urllib2.urlopen(self.url, args_enc)
        except urllib2.HTTPError, e:
            # Check for for Forbidden HTTP status, which means invalid API key.
            if e.code == 403:
                return ['Invalid API key.']
            return ['error %i' % e.code]

        output = json.loads(response.read())
        results =[]
        try:
             results = [kw['Name'] for kw in output['ns1:TopicsResponse']['TopicsReturn']['Topics']['Locations']]
        except KeyError:
            pass
        try:
            results += [kw['Topic']['Name'] for kw in output['ns1:TopicsResponse']['TopicsReturn']['Topics']['TopTopics']]
        except KeyError:
            pass
        return results
