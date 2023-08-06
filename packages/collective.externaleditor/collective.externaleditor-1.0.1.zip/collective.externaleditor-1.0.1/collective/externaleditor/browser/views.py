from Acquisition import aq_parent, aq_inner
from zope.component import queryUtility
from zExceptions import Unauthorized

from Products.Five import BrowserView
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.utils import webdav_enabled
from Products.CMFPlone.interfaces import IPloneSiteRoot
from Products.PythonScripts.standard import url_quote
from Products.statusmessages.interfaces import IStatusMessage

from collective.externaleditor.browser.controlpanel import IExternalEditorSchema
from collective.externaleditor import ExternalEditorMessageFactory as _


class ExternalEditorEnabledView(BrowserView):
    """
    """
    def available(self, bypasslock = False):
        """
        """
        return (self.isEnabledOnThisContentType()
                and self.isActivatedInMemberProperty()
                and self.isActivatedInSiteProperty()
                and self.isWebdavEnabled()
                and not (self.isObjectLocked() and not bypasslock)
                and not self.isObjectTemporary()
                and not self.isStructuralFolder()
                and self.isExternalEditLink_())

    @property
    def _options(self):
        """
        """
        #
        return queryUtility(IPloneSiteRoot)

    def portalTypesAware(self):
        """
        """
        #
        return getattr(IExternalEditorSchema(self._options), 'externaleditor_enabled_types', [])

    def isEnabledOnThisContentType(self):
        """
        """
        #
        if self.context.portal_type not in self.portalTypesAware():
            return False
        #
        return True

    def isActivatedInMemberProperty(self):
        """
        """
        #
        mtool = getToolByName(self.context, 'portal_membership')
        #
        if mtool.isAnonymousUser():
            return False
        # Check if the member property
        member = mtool.getAuthenticatedMember()
        if not member.getProperty('ext_editor', False):
            return False
        #
        return True

    def isActivatedInSiteProperty(self):
        """
        """
        #
        return getattr(IExternalEditorSchema(self._options), 'ext_editor', False)

    def isObjectLocked(self):
        """
        """
        # note: you may comment out those two lines if you prefer to let the user to borrow the lock
        if self.context.wl_isLocked():
            return True
        #
        return False

    def isWebdavEnabled(self):
        """
        """
        #
        if not webdav_enabled(self.context, aq_parent(aq_inner(self.context))):
            return False
        #
        return True

    def isObjectTemporary(self):
        """
        """
        # Temporary content cannot be changed through EE (raises AttributeError)
        portal_factory = getToolByName(self.context, 'portal_factory')
        #
        if portal_factory.isTemporary(self.context):
            return True
        #
        return False

    def isStructuralFolder(self):
        """
        """
        #
        state = self.context.restrictedTraverse("@@plone_context_state")
        #
        if state.is_structural_folder():
            return True
        #
        return False

    def isExternalEditLink_(self):
        """
        """
        #
        portal = getToolByName(self.context, 'portal_url').getPortalObject()
        # Content may provide data to the external editor ?
        return not not portal.externalEditLink_(self.context)


class ExternalEditView(ExternalEditorEnabledView):
    """
    """
    def __call__(self):
        """
        """
        #
        if self.available(bypasslock = True):
            return self.context.REQUEST['RESPONSE'].redirect(
                '%s/externalEdit_/%s.zem' % (aq_parent(aq_inner(self.context)).absolute_url(),
                                         url_quote(self.context.getId())))
        #
        if not self.isActivatedInSiteProperty():
            status = _(u"External Editor site property is not activated. Please contact your administrator.")
        elif not self.isActivatedInMemberProperty():
            status = _(u"External Editor property in your preferences is not activated.")
        elif self.isObjectLocked():
            status = _(u"This item is locked.")
        else :
            status = _(u"You are not allowed to use External Editor on this item.")
        #
        redirecturl = self.context.absolute_url()+'/view'
        self.request.response.redirect(redirecturl)
        IStatusMessage(self.request).addStatusMessage(status, type='error')
