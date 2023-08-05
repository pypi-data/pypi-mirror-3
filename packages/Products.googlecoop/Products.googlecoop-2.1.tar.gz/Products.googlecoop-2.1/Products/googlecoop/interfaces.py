from zope import interface, schema

from Products.googlecoop import googlecoopMessageFactory as _


class IGoogleCoopSettingsSchema(interface.Interface):

    googleapi = schema.TextLine(
       title=_(u"Google API Code"),
       description=_(u"""You need your own API key in order to use this API.
                The default key provided below is only valid for loclahost:8080.
                Replace it with your own, unique key."""),
       default=u"ABQIAAAAaKes6QWqobpCx2AOamo-shTwM0brOpm-All5BF6PoaKBxRWWERSUWbHs4SIAMkeC1KV98E2EdJKuJw",
       required=True)


    identifier = schema.TextLine(
        title=_(u'Identifier'),
        description=_(u"""Your Custom Search Engine's unique identifier.
                    If you leave this empty Custom Search automatically
                    restricts searches to the current site"""),
        required=True,
        readonly=False,
        default=u'009744842749537478185:hwbuiarvsbo',
        )

    adstatus = schema.Bool(
        title=_(u'Non profit'),
        description=_(u"""Advertising status. Specify whether your search engine is for a
            non-profit, university, or government website that should not
            have advertising on the results pages."""),
        required=False,
        readonly=False,
        default=False,
        )

    adsposition = schema.Choice(
        title=_(u'Show ads on results pages'),
        description=_(u"""Specify where in the results you want advertising
            to be placed (if enabled)."""),
        required=True,
        readonly=False,
        vocabulary='googlecoop.showadsvocab',
        default=u'FORID:9',
        )


    domain = schema.TextLine(
        title=_(u'Google Domain'),
        description=_(u"""You can choose a different Google domain than
            google.com (such as google.ru or google.es). This makes your
            search results favor results from that country."""),
        required=True,
        readonly=False,
        default=u'www.google.com',
        )

    autocomplete = schema.Bool(
        title=_(u'Enable autocompletions'),
        description=_(u"""As you type into your search engine's search box,
            Autocomplete offers searches similar to the one you're typing."""),
        required=False,
        readonly=False,
        default=True,
        )

    nocss = schema.Bool(
        title=_(u'Do not load google css'),
        description=_(u"""If you don't intend to use the default CSS
                from google but rather define your own"""),
        required=False,
        readonly=False,
        default=False,
        )


    labelkeywords = schema.Bool(
        title=_(u'Use Keywords'),
        description=_(u"""Use your sites keywords as labels for the CSE."""),
        required=False,
        readonly=False,
        default=True,
        )

    cse_content_types = schema.List(
        title = _(u'CSE content types'),
        required = False,
        default = [u'Link', u'Event'],
        description = _(u"A list of types that can be used to build a CSE",),
        value_type = schema.Choice(title=_(u"Content types"),
                    source="plone.app.vocabularies.ReallyUserFriendlyTypes"))

    exclude_domains = schema.List(
        title = _(u'Exclude domains'),
        required = False,
        description = _(u"Blacklist domains to be excluded from your CSEs",),
        value_type = schema.Choice(title=_(u"Domain blacklist"),
                    source="googlecoop.excludedomainsvocab"))



