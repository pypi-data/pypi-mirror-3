from zope.interface import implements
from zope import schema
from zope.formlib import form
from plone.portlets.interfaces import IPortletDataProvider
from plone.app.portlets.portlets import base
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from Products.CMFPlone import PloneMessageFactory as _
#from Products.CMFCore.utils import getToolByName

from status import StatusViewlet


class IMicroblogPortlet(IPortletDataProvider):
    """A portlet to render the microblog.
    """

    title = schema.TextLine(title=_(u"Title"),
                            description=_(u"A title for this portlet"),
                            required=True,
                            default=u"Microblog")

    compact = schema.Bool(title=_(u"Compact rendering"),
                          description=_(u"Hide portlet header and footer"),
                          default=True)


class Assignment(base.Assignment):
    implements(IMicroblogPortlet)

    title = u""  # overrides readonly property method from base class

    def __init__(self, title, compact):
        self.title = title
        self.compact = compact


class Renderer(base.Renderer):

    def __init__(self, context, request, view, manager, data):
        base.Renderer.__init__(self, context, request, view, manager, data)
        self._statusviewlet = StatusViewlet(data.compact,
                                            context, request, view, manager)

    @property
    def available(self):
        return True

    @property
    def compact(self):
        return self.data.compact

    def update(self):
        self._statusviewlet.update()

    render = ViewPageTemplateFile('microblog.pt')

    def statusform(self):
        return self._statusviewlet.render()


class AddForm(base.AddForm):
    form_fields = form.Fields(IMicroblogPortlet)

    def create(self, data):
        return Assignment(**data)


class EditForm(base.EditForm):
    form_fields = form.Fields(IMicroblogPortlet)
