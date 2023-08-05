from zope.interface import implements, Interface

from Products.Five import BrowserView
from Products.CMFCore.utils import getToolByName

from collective.taghelper import taghelperMessageFactory as _


class IFileHtmlPreviewView(Interface):
    """
    FileHtmlPreview view interface
    """



class FileHtmlPreviewView(BrowserView):
    """
    FileHtmlPreview browser view
    """
    implements(IFileHtmlPreviewView)

    def __init__(self, context, request):
        self.context = context
        self.request = request

    def get_html(self):
        portal_transforms = getToolByName(self.context, 'portal_transforms')
        try:
            html = portal_transforms.convertTo('text/html',
                self.context.data,
                mimetype=self.context.get_content_type).getData()
        except AttributeError:
            html = '<h1> %s </h1> <p> %s </p>' %(self.context.Title(),
                    self.context.Description())
        return html
