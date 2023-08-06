import Acquisition
from Products.Five.browser import BrowserView
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from Products.CMFCore.utils import getToolByName
from slc.linkcollection.browser.viewlets import LinkBoxViewlet

class LinkcollectionView(BrowserView, LinkBoxViewlet):
    """View for displaying the contents of a Linkcollection, e.g. on a folder
    """
    template = ViewPageTemplateFile('linkcollection_view.pt')
    template.id = "linkcollection-view"

    def __call__(self):

        return self.template()
