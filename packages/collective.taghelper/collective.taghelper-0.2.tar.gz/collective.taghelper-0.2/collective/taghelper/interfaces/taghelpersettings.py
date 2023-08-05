from zope import interface, schema

from collective.taghelper import taghelperMessageFactory as _

class ITagHelperSettingsSchema(interface.Interface):
    # -*- extra stuff goes here -*-

    calais_api_key = schema.TextLine(
        title=u'Open Calais API Key',
        description=u'API Key can be obtained at http://www.opencalais.com/APIkey',
        required=False,
        readonly=False,
        default=None,
        )

    yahoo_api_key = schema.TextLine(
        title=u'Yahoo API Key',
        description=u'API Key can be obtained at http://developer.apps.yahoo.com/dashboard/createKey.html',
        required=False,
        readonly=False,
        default=None,
        )

    silcc_api_key = schema.TextLine(
        title=u'SiLCC API Key',
        description=u'API Key can be obtained at http://opensilcc.com/',
        required=False,
        readonly=False,
        default=None,
        )


    silcc_url = schema.TextLine(
        title=u'SiLCC server URL',
        description=u'Enter the url of your silcc server',
        required=False,
        readonly=False,
        default=u'http://opensilcc.com/api/tag',
        )

    alchemy_api_key = schema.TextLine(
        title=u'AlchemyAPI Key',
        description=u'API Key can be obtained at http://www.alchemyapi.com/api/register.html',
        required=False,
        readonly=False,
        default=None,
        )



    use_remote_url = schema.Bool(
        title=u'Use remote url',
        description=u'''If the content item has a remote url
                        extract the tags from there rather than
                        from the local content (Yahoo, AlchemyAPI and tagthe.net only)''',
        required=False,
        readonly=False,
        default=True,
        )

    webservices = schema.List(
        title = _(u'Use webservices'),
        required = False,
        default = [],
        description = _(u"List the webservices you want to use for tagging"),
        value_type = schema.Choice(title=_(u"webservices"),
                    source="collective.taghelper.webservices"))
