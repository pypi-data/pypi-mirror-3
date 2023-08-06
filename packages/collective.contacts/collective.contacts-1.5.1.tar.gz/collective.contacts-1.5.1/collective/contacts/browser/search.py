from Acquisition import aq_inner, aq_parent
from AccessControl import Unauthorized

from zope.component import queryAdapter
from plone.memoize.instance import memoize

from Products.statusmessages.interfaces import IStatusMessage
from Products.CMFCore.utils import getToolByName, _checkPermission
from Products.CMFCore.permissions import ModifyPortalContent
from Products.CMFPlone.PloneBatch import Batch

from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile

from collective.contacts.browser.list import AbstractListView
from collective.contacts.interfaces import IAddressBook, IExport
from collective.contacts import contactsMessageFactory as _

class AbstractSearchView(AbstractListView):
    """ Displays search results
    """
    template = ViewPageTemplateFile('./templates/search.pt')
        
    def __call__(self):
        self.request.set('disable_border', 1)
        # redirect on cancel
        if self.request.get('form.actions.label_cancel'):
            return self.request.response.redirect('%s/list_%ss' % (self.context.absolute_url(), self.name))
        
        # redirect on import
        if self.request.get('form.button.import', None) is not None:
            parent = aq_inner(self.context)
            while not IAddressBook.providedBy(parent):
                parent = aq_parent(parent)
            if not _checkPermission(ModifyPortalContent, parent):
                raise Unauthorized
            return self.request.response.redirect('%s/import' % parent.absolute_url())
        
        self.error = None
        self.quick = self.request.get('quicksearch', None) is not None
        mail = self.request.get('form.button.mailto', None) is not None
        export = self.request.get('form.button.export', None) is not None
        exportall = self.request.get('form.button.exportall', None) is not None
        exportsearch = self.request.get('form.button.exportsearch', None) is not None
        exportformat = self.request.get('form.exportformat', 'csv')
        advanced = self.request.get('form.button.advanced', None) is not None
        
        rows = self.table.rows()
        self.batch = Batch(rows, self.page_size, self.request.form.get('b_start', 0))
        
        selection = self.get_selection()
        
        if (export or mail) and not selection:
            self.error = _(u'You need to select at least one person or organization')
        elif mail:
            self.mailto = self.get_mailto(selection)
            if not self.mailto.strip():
                self.error = _(u'You need to select at least one person or organization that has an email')
        elif export or exportall or exportsearch:
            if exportsearch:
                selection = [row['object'] for row in rows]
            handler = queryAdapter(self.context, interface=IExport, name=exportformat)
            if handler is None:
                handler = queryAdapter(self.context, interface=IExport, name='%s.csv' % self.name)
            return handler.export(self.request, (export or exportsearch) and selection or None)
        elif advanced:
            return self.request.RESPONSE.redirect(self.advanced_url())
        
        if self.error:
            statusmessage = IStatusMessage(self.request)
            statusmessage.addStatusMessage(self.error, 'error')
            return self.request.response.redirect(self.back_url())
        
        return self.template()
    
    @memoize
    def get_selection(self):
        if self.request.form.get('selection', None) is None:
            return []
        catalog = getToolByName(self.context, 'portal_catalog')
        results = catalog(UID=self.request.form.get('selection', []))
        return [brain.getObject() for brain in results]
    
    def get_mailto(self, selection):
        emails = []
        for object in selection:
            email = self.table.email(object)
            if email:
                emails.extend(email.split(', '))
        return ', '.join(set(emails))
    
    @memoize
    def customize_url(self):
        if getattr(self, 'mailto', None):
            return None
        return super(AbstractSearchView, self).customize_url()
    
    @memoize
    def back_url(self):
        return '%s/%s' % (self.context.absolute_url(), self.request.get('form.camefrom', 'list_%ss' % self.name))

class PersonSearchView(AbstractSearchView):
    """ Displays person search results
    """
    template_id = 'search_person'
    name = 'person'
    page_size = 20

class OrganizationSearchView(AbstractSearchView):
    """ Displays organization search results
    """
    template_id = 'search_organization'
    name = 'organization'
    page_size = 20

class GroupSearchView(AbstractSearchView):
    """ Displays group search results
    """
    template_id = 'search_group'
    name = 'group'
    page_size = 20
