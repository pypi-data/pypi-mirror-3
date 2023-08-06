from zope.interface import Interface

from zope.interface import implements
from zope.component import getMultiAdapter


from plone.portlets.interfaces import IPortletDataProvider
from plone.app.portlets.portlets import base

from zope import schema
from zope.formlib import form
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from plone.memoize.instance import memoize

from collective.tagcloud import TagCloudMessageFactory as _
from Products.CMFPlone.utils import getToolByName

class ITagCloudPortlet(IPortletDataProvider):
    """A portlet

    It inherits from IPortletDataProvider because for this portlet, the
    data that is being rendered and the portlet assignment itself are the
    same.
    """

    # TODO: Add any zope.schema fields here to capture portlet configuration
    # information. Alternatively, if there are no settings, leave this as an
    # empty interface - see also notes around the add form and edit form
    # below.

    # options for generating tag cloud data

    smallest = schema.Int(
        title=_(u'Smallest tag size'),
        description=_(u'Text size of the tag with the smallest count value (in percentage of default font size).'),
        required=True,
        default=100)

    largest = schema.Int(
        title=_(u'Largest tag size'),
        description=_(u'Text size of the tag with the highest count value (in percentage of default font size).'),
        required=True,
        default=300)

    max_tags = schema.Int(
        title=_(u'Maximum number of tags to display'),
        description=_(u'Used when too many tags spoil the display.'),
        required=True,
        default=50)



class Assignment(base.Assignment):
    """Portlet assignment.

    This is what is actually managed through the portlets UI and associated
    with columns.
    """

    implements(ITagCloudPortlet)

    # TODO: Set default values for the configurable parameters here

    smallest=100
    largest=300
    max_tags=50

    def __init__(self, **kw):
        for k, v in kw.items():
            setattr(self, k, v)

    @property
    def title(self):
        """This property is used to give the title of the portlet in the
        "manage portlets" screen.
        """
        return "Tag Cloud portlet"

class Renderer(base.Renderer):
    """Portlet renderer.

    This is registered in configure.zcml. The referenced page template is
    rendered, and the implicit variable 'view' will refer to an instance
    of this class. Other methods can be added and referenced in the template.
    """

    render = ViewPageTemplateFile('portlet.pt')

    def __init__(self, context, request, view, manager, data):
        base.Renderer.__init__(self, context, request, view, manager, data)
        portal_state = getMultiAdapter((context, request), name=u'plone_portal_state')
        self.portal_url = portal_state.portal_url()
        portal_properties = getMultiAdapter((context, request), name=u'plone_tools').properties()
        self.default_charset = portal_properties.site_properties.getProperty('default_charset', 'utf-8')


    def calcTagSize(self, number, min_d, max_d):
        rc = float(self.data.largest-self.data.smallest)
        rc *= float(number-min_d)
        rc /= float(max_d-min_d)
        rc += float(self.data.smallest)
        return int(rc)

    @memoize
    def subjects(self):
        pc = getToolByName(self.context, 'portal_catalog')
        total = 0
        d = {}
        for result in pc():
            for subject in result.Subject or []:
                if subject not in d: d[subject] = 0
                d[subject] += 1
                total += 1
        d_val = d.values()
        if d_val:
            d_val.sort()
            if len(d_val) > self.data.max_tags:
                min_d = d_val[-self.data.max_tags]
            else:
                min_d = d_val[0]
            max_d = d_val[-1] 
        else:
            min_d = max_d = 0
        d_keys = [ x for x in d.keys() if d[x] >= min_d ]
        d_keys.sort()
        l = [ (x, self.calcTagSize(d[x], min_d, max_d),
                   'search?Subject%3Alist=' + x ) for x in d_keys ]
        return l[:self.data.max_tags]


# NOTE: If this portlet does not have any configurable parameters, you can
# inherit from NullAddForm and remove the form_fields variable.

class AddForm(base.AddForm):
    """Portlet add form.

    This is registered in configure.zcml. The form_fields variable tells
    zope.formlib which fields to display. The create() method actually
    constructs the assignment that is being added.
    """
    form_fields = form.Fields(ITagCloudPortlet)

    def create(self, data):
        return Assignment(**data)

# NOTE: IF this portlet does not have any configurable parameters, you can
# remove this class definition and delete the editview attribute from the
# <plone:portlet /> registration in configure.zcml

class EditForm(base.EditForm):
    """Portlet edit form.

    This is registered with configure.zcml. The form_fields variable tells
    zope.formlib which fields to display.
    """
    form_fields = form.Fields(ITagCloudPortlet)
