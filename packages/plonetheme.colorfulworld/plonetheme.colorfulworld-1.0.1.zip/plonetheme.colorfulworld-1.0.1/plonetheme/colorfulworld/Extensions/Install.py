from Products.CMFCore.utils import getToolByName


def uninstall(portal, reinstall=False):
    setup_tool = getToolByName(portal, 'portal_setup')
    setup_tool.runAllImportStepsFromProfile('profile-plonetheme.colorfulworld:uninstall')
    return "Ran all uninstall steps."