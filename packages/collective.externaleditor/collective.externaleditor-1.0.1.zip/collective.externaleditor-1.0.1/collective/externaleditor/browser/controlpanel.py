from zope.interface import Interface
from zope.component import adapts
from zope.formlib import form
from zope.interface import implements
from zope.schema import List
from zope.schema import Bool
from zope.schema import Tuple
from zope.schema import Choice

from Products.CMFCore.utils import getToolByName
from Products.CMFDefault.formlib.schema import ProxyFieldProperty
from Products.CMFDefault.formlib.schema import SchemaAdapterBase
from Products.CMFPlone.interfaces import IPloneSiteRoot

from plone.app.controlpanel.form import ControlPanelForm

from collective.externaleditor import ExternalEditorMessageFactory as _

class IExternalEditorSchema(Interface):
    """
    """
    ext_editor = Bool(
        title = _(u"label_externaleditor_enabled",
                  default=u"Enable External Editor feature"),
        description = _(u"help_externaleditor_enabled",
                        default=u"Determines if the External Editor feature "
                                "is enabled. This feature requires a special "
                                "client-side application installed. The users "
                                "also have to enable this in their "
                                "preferences."),
        default=True,
        required=False)

    externaleditor_enabled_types = List(
        title = _(u"label_externaleditor_enabled_types",
                  default=u"Content types editable with External Editor"),
        required = False,
        default = ['File', 'Image', ],
        description = _(u"help_externaleditor_enabled_types",
                        default=u"Choose here the content types where the "
                                "External Editor action will be available"),
        value_type = Choice(title=u"externaleditor_enabled_types",
                            source="plone.app.vocabularies.ReallyUserFriendlyTypes"))


class ExternalEditorControlPanelAdapter(SchemaAdapterBase):
    """
    """
    adapts(IPloneSiteRoot)
    implements(IExternalEditorSchema)

    def __init__(self, context):
        super(ExternalEditorControlPanelAdapter, self).__init__(context)

    ext_editor = ProxyFieldProperty(IExternalEditorSchema['ext_editor'])
    externaleditor_enabled_types = ProxyFieldProperty(IExternalEditorSchema['externaleditor_enabled_types'])


class ExternalEditorControlPanel(ControlPanelForm):
    """
    """
    form_fields = form.FormFields(IExternalEditorSchema)

    label = _("External Editor settings")
    description = _("External Editor settings.")
    form_name = _("External Editor settings")
