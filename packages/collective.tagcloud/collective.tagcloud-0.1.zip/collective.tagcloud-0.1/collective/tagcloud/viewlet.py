from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from plone.app.layout.viewlets.common import ViewletBase


class TagCloudViewlet(ViewletBase):
    render = ViewPageTemplateFile('viewlet.pt')



