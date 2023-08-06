# -*- coding: utf-8 -*-
from zope.interface import implements

from plone.portlets.interfaces import IPortletDataProvider
from plone.app.portlets.portlets import base

from zope import schema

from zope.formlib import form
from zope.schema.vocabulary import SimpleVocabulary, SimpleTerm

from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile

#from plone.registry.interfaces import IRegistry
#from collective.prettydate.interfaces import IPrettyDate

from collective.facebook.portlets.config import PROJECTNAME

from zope.security import checkPermission

from collective.facebook.portlets import _

import logging

logger = logging.getLogger(PROJECTNAME)

color_scheme = SimpleVocabulary(
    [SimpleTerm(value=u'light', title=_(u'Light')),
     SimpleTerm(value=u'dark', title=_(u'Dark'))]
    )

target = SimpleVocabulary(
    [SimpleTerm(value=u'_blank', title=_(u'_blank')),
     SimpleTerm(value=u'_top', title=_(u'_top')),
     SimpleTerm(value=u'_parent', title=_(u'_parent'))]
    )


class IFacebookActivityPortlet(IPortletDataProvider):
    """A portlet

    It inherits from IPortletDataProvider because for this portlet, the
    data that is being rendered and the portlet assignment itself are the
    same.
    """

    header = schema.TextLine(title=_(u'Header'),
                             description=_(u"The header for the portlet. "
                                            "Leave empty for none."),
                             required=False)

    api_key = schema.TextLine(title=_(u'API key'),
                             description=_(u"The key for the app to be used."),
                             required=True)

    api_key = schema.TextLine(title=_(u'API key'),
                             description=_(u"The key for the app to be used."),
                             required=True)

    site_url = schema.TextLine(title=_(u'Site URL'),
                             description=_(u"The site URL for which you want "
                                            "to show the activity feed. it "
                                            "defaults to the current URL"),
                             required=False)

    recommendations = schema.Bool(title=_(u'Show recommendations'),
                            description=_(u"Allow the portlet to show "
                                           "recommendations."),
                            required=False)

    width = schema.Int(title=_(u'Width'),
                       description=_(u"Width of the portlet."),
                       required=True,
                       default=300)

    height = schema.Int(title=_(u'Height'),
                             description=_(u"Height of the portlet."),
                             required=True,
                             default=300)

    color_scheme = schema.Choice(title=_(u'Color Scheme'),
                                 description=_(u"The color scheme to use"),
                                 required=True,
                                 vocabulary=color_scheme)

    target = schema.Choice(title=_(u'Target'),
                           description=_(u"The target to open links."),
                           required=True,
                           vocabulary=target)

    border_color = schema.TextLine(title=_(u'Border color'),
                             description=_(u"The border color to use (hex)."),
                             required=False)


class Assignment(base.Assignment):
    """Portlet assignment.

    This is what is actually managed through the portlets UI and associated
    with columns.
    """

    implements(IFacebookActivityPortlet)

    header = u""
    api_key = u""
    site_url = u""
    recommendations = False
    width = 300
    height = 300
    color_scheme = u"light"
    target = u"_blank"
    border_color = u""

    def __init__(self,
                 api_key,
                 site_url,
                 recommendations=False,
                 header=u"",
                 width=300,
                 height=300,
                 color_scheme=u"light",
                 target=u"_blank",
                 border_color=u""):

        self.header = header
        self.api_key = api_key
        self.site_url = site_url
        self.recommendations = recommendations
        self.width = width
        self.height = height
        self.color_scheme = color_scheme
        self.target = target
        self.border_color = border_color

    @property
    def title(self):
        """This property is used to give the title of the portlet in the
        "manage portlets" screen.
        """
        return _(u"Facebook activity feed")


class Renderer(base.Renderer):
    """Portlet renderer.

    This is registered in configure.zcml. The referenced page template is
    rendered, and the implicit variable 'view' will refer to an instance
    of this class. Other methods can be added and referenced in the template.
    """

    render = ViewPageTemplateFile('fbactivity.pt')

    def getHeader(self):
        """
        Returns the header for the portlet
        """
        return self.data.header

    def canEdit(self):
        return checkPermission('cmf.ModifyPortalContent', self.context)

    def getJsCode(self):

        js_code = """
        (function(d, s, id) {
            var js, fjs = d.getElementsByTagName(s)[0];
            if (d.getElementById(id)) return;
            js = d.createElement(s); js.id = id;
            js.src = "//connect.facebook.net/en_US/all.js#xfbml=1&appId=%s";
            fjs.parentNode.insertBefore(js, fjs);
            }(document, 'script', 'facebook-jssdk'));
            """ % self.data.api_key

        return js_code

    #def getDate(self, str_date):
        #if self.data.pretty_date:
            ## Returns human readable date for the wall post
            #date_utility = getUtility(IPrettyDate)
            #date = date_utility.date(str_date)
        #else:
            #date = DateTime(str_date)

        #return date


class AddForm(base.AddForm):
    """Portlet add form.

    This is registered in configure.zcml. The form_fields variable tells
    zope.formlib which fields to display. The create() method actually
    constructs the assignment that is being added.
    """
    form_fields = form.Fields(IFacebookActivityPortlet)

    def create(self, data):
        return Assignment(**data)


class EditForm(base.EditForm):
    """Portlet edit form.

    This is registered with configure.zcml. The form_fields variable tells
    zope.formlib which fields to display.
    """
    form_fields = form.Fields(IFacebookActivityPortlet)
