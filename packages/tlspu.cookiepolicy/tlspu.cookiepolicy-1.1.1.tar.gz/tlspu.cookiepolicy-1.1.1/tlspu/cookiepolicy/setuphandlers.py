from Products.CMFCore.utils import getToolByName

def install(context):

    # Ordinarily, GenericSetup handlers check for the existence of XML files.
    # Here, we are not parsing an XML file, but we use this text file as a
    # flag to check that we actually meant for this import step to be run.
    # The file is found in profiles/default.

    if context.readDataFile('tlspu.cookiepolicy_install.txt') is None:
        return

    # Add additional setup code here

def uninstall(context):

    if context.readDataFile('tlspu.cookiepolicy_uninstall.txt') is None:
        return

    portal = context.getSite()
    portal_conf = getToolByName(portal, 'portal_controlpanel')
    portal_conf.unregisterConfiglet('@@likes-providers')

    # Remove tweetmeme_properties in portal properties
    pp = getToolByName('portal_properties')

    try:
        if hasattr(pp, 'tlspu_cookiepolicy_properties'):
            pp.manage_delObjects(ids='tlspu_cookiepolicy_properties')
    except KeyError:
        pass

