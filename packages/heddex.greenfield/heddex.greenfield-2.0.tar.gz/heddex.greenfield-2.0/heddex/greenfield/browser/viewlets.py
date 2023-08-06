from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from plone.app.layout.viewlets.common import ViewletBase

from plone.app.layout.viewlets import common

class SearchBoxViewlet(common.SearchBoxViewlet):
    """A custom version of the searchbox class
    """
    render = ViewPageTemplateFile('searchbox.pt')
