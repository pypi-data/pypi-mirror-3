from zope import interface, schema, component
#from z3c.form import form, field, button
#from plone.z3cform.layout import wrap_form
from DateTime import DateTime
from persistent import Persistent

from zope.app.form import CustomWidgetFactory
from zope.app.component.hooks import getSite
from zope.annotation import factory
from zope.annotation.interfaces import IAnnotations, IAttributeAnnotatable, IAnnotatable
from zope.component import adapts
from zope.formlib import form
from zope.interface import Interface, implements
from zope.interface.common import idatetime

from Products.ATContentTypes.interface import IATDocument, IATFolder
from Products.CMFCore.utils import getToolByName

from plone.app.form.widgets.uberselectionwidget import UberSelectionWidget, UberMultiSelectionWidget
from plone.app.vocabularies.catalog import SearchableTextSourceBinder

from slc.linkcollection.interfaces import ILinkList, ILinkListDocument, ILinkListFolder
from slc.linkcollection import LinkCollectionMessageFactory as _


class LinkListBase(Persistent):
    implements(ILinkList)

    @property
    def portal_catalog(self):        
        """ make the adapter penetratable for the vocabulary to find the cat"""
        return getToolByName(getSite(), 'portal_catalog')

    @property
    def portal_url(self):        
        """ make the adapter penetratable for the vocabulary to find the cat"""
        return getToolByName(getSite(), 'portal_url')
        
    urls = []
  
    
class LinkList(LinkListBase):
    implements(ILinkList, ILinkListDocument)
    adapts(IATDocument)

linklist_adapter_document = factory(LinkList)

class LinkListFolder(LinkListBase):
    implements(ILinkList, ILinkListFolder)
    adapts(IATFolder)

linklist_adapter_folder = factory(LinkListFolder)

class LinkCollectionForm(form.PageEditForm):
    form_fields = form.Fields(ILinkList)
    label = u"Add Content Objects to point to"
    form_fields['urls'].custom_widget = UberMultiSelectionWidget

    @form.action(_("Apply"))
    def handle_edit_action(self, action, data):
        ILinkList(self.context).urls = data['urls']

        status = _("Updated on ${date_time}",
                   mapping={'date_time': DateTime()}
                   )
        self.status = status

LinkCollectionView = LinkCollectionForm

