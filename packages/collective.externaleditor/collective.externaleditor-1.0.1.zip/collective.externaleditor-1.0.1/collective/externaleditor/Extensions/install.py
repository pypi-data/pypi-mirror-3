from StringIO import StringIO
from Products.CMFCore.utils import getToolByName


def uninstall(portal):
    #
    out = StringIO()
    #
    setup_tool = getToolByName(portal, 'portal_setup')
    setup_tool.runAllImportStepsFromProfile('profile-collective.externaleditor:uninstall')
    out.write('Ran all uninstall steps.')
    # Uninstall configlet
    configTool = getToolByName(portal, 'portal_controlpanel', None)
    if configTool:
        out.write('Removing configlet %s\n' % 'collective.externaleditor')
        configTool.unregisterConfiglet('collective.externaleditor')
    #
    return out.getvalue()
