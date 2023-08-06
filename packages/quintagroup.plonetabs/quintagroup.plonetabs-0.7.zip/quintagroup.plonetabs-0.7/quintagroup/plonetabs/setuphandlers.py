from Products.CMFCore.utils import getToolByName

def cleanUpControlPanel(portal, out):
    cpt = getToolByName(portal, 'portal_controlpanel')
    if 'plonetabs' in [o.id for o in cpt.listActions()]:
        cpt.unregisterConfiglet('plonetabs')
        out.append('plonetabs configlet unregistered.')

def uninstall(context):
    # Only run step if a flag file is present (e.g. not an extension profile)
    if context.readDataFile('quintagroup.plonetabs-uninstall.txt') is None:
        return
    out = []
    site = context.getSite()
    
    cleanUpControlPanel(site, out)
