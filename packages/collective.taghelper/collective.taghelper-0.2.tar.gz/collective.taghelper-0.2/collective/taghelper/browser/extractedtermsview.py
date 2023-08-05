from zope.interface import implements, Interface
from zope.component import getUtility

from Products.Five import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from Products.CMFCore.utils import getToolByName

from plone.registry.interfaces import IRegistry
from collective.taghelper.interfaces import ITagHelperSettingsSchema
from collective.taghelper import taghelperMessageFactory as _
from collective.taghelper.utilities import get_yql_subjects
from collective.taghelper.utilities import get_yql_subjects_remote
from collective.taghelper.utilities import get_calais_subjects
from collective.taghelper.utilities import get_silcc_subjects
from collective.taghelper.utilities import get_ttn_subjects
from collective.taghelper.utilities import get_ttn_subjects_remote
from collective.taghelper.utilities import get_alchemy_subjects
from collective.taghelper.utilities import get_alchemy_subjects_remote
from collective.taghelper.interfaces import ITagHelperSettingsSchema

class IExtractedTermsView(Interface):
    """
    ExtractedTerms view interface
    """

class ExtractedTermsView(BrowserView):
    """
    ExtractedTerms browser view
    """
    implements(IExtractedTermsView)

    template = ViewPageTemplateFile('extractedtermsview.pt')
    use_remote_url = False
    url = ''

    js_template = '''
        $.get('%(url)s',
                function(data) {
                  $('#%(id)s').html(data);
            });
            '''
    def __init__(self, context, request):
        self.context = context
        self.request = request


    def services(self):
        registry = getUtility(IRegistry)
        settings = registry.forInterface(ITagHelperSettingsSchema)
        active_services = settings.webservices
        slist=[]
        for service in active_services:
            sname = service.replace(' ','').replace('.', '').lower()
            slist.append({'sid': sname, 'name': service})
        return slist

    def get_js(self, service):
        vars = {}
        url = '/@@tagsnippets.html?service='
        vars['url'] = self.context.absolute_url() + url + service
        vars['id'] = 'results-' + service
        return self.js_template % vars


    def __call__(self):
        form = self.request.form
        if form.has_key('form.button.save'):
            keywords = list(self.context.Subject())
            keywords = keywords + form.get('subject', [])
            keywords=list(set(keywords))
            self.context.setSubject(keywords)
            self.request.response.redirect(self.context.absolute_url() + '/edit')
            return ''
        elif form.has_key('form.button.cancel'):
            self.request.response.redirect(self.context.absolute_url() + '/view')
            return ''
        return self.template()


class IETSnippetView(Interface):
    """
    ExtractedTerms Result Snippets view interface
    """

class ETSnippetView(BrowserView):
    """
    ExtractedTerms Result Snippets browser view
    """
    implements(IETSnippetView)

    template = ViewPageTemplateFile('etsnippetview.pt')
    use_remote_url = False
    url = ''

    def __init__(self, context, request):
        registry = getUtility(IRegistry)
        settings = registry.forInterface(ITagHelperSettingsSchema)
        self.use_remote_url = settings.use_remote_url
        self.context = context
        self.request = request
        if self.context.portal_type == 'File':
            self.url = self.request.URL1 +'/filehtmlpreview_view'
        elif hasattr(self.context, 'getRemoteUrl'):
            if self.use_remote_url and self.context.getRemoteUrl():
                self.url = self.context.getRemoteUrl()
            else:
                self.url = self.request.URL1 +'?ajax_load=1'
        if not self.url:
            self.url = self.request.URL1 +'?ajax_load=1'
        self.text = self._get_text()

    def _get_text(self):
        if hasattr(self.context, 'SearchableText'):
            return self.context.SearchableText()
        else:
            return ''


    @property
    def service_id(self):
        return self.request.form.get('service', '')

    def terms(self):
        sid = self.service_id
        if sid=='tagthenet':
            if self.use_remote_url:
                tags = get_ttn_subjects_remote(self.url)
            else:
                tags = get_ttn_subjects(self.text)
        elif sid=='alchemyapi':
            if self.use_remote_url:
                tags = get_alchemy_subjects_remote(self.url)
            else:
                tags = get_alchemy_subjects(self.text)
        elif sid=='yahoo':
            if self.use_remote_url:
                tags = get_yql_subjects_remote(self.url)
            else:
                 tags = get_yql_subjects(self.text)

        elif sid=='opencalais':
            tags = get_calais_subjects(self.text, self.context.UID())
        elif sid=='sillc':
            text = self.context.Title() + '. ' + self.context.Description()
            tags = get_silcc_subjects(text)
        else:
            return []
        keywords = list(self.context.Subject())
        for kw in keywords:
            if kw in tags:
                tags.remove(kw)
        return tags


    def tos(self):
        sid = self.service_id
        if sid=='tagthenet':
            t = """<a href="http://www.tagthe.net/faq"> Terms of use </a>
            """
        elif sid=='alchemyapi':
            t = """<a href="http://www.alchemyapi.com/company/terms.html" >Terms of Use
            <img src="http://www.alchemyapi.com/images/alchemyAPI.jpg" alt="AlchemyAPI" />
            </a>
            """
        elif sid=='yahoo':
            t = """ <a href="http://info.yahoo.com/legal/us/yahoo/yql/yql-4307.html">
            Yahoo! Query Language Terms Of Use</a>"""
        elif sid=='opencalais':
            t =""" <a href = "http://www.opencalais.com/terms"> Calais Web Service Terms of Service
            <img src="http://www.opencalais.com/files/wpro_shared/images/Calais%20icon_16x16.jpg"
                alt="Open Calais" title="Calais powered by Thomson Reuters" />
            </a>"""
        elif sid=='sillc':
            t = ''
        else:
            t = ''
        return t

    def __call__(self):
        self.request.response.setHeader('X-Theme-Disabled', 'True')
        return self.template()


