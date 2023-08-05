from Products.CMFCore.utils import getToolByName

def remove_action_icons(site):
    ai = getToolByName(site, 'portal_actionicons')
    if ai.queryActionIcon('controlpanel', 'uwosh-northstar'):
        ai.removeActionIcon('controlpanel', 'uwosh-northstar')
    if ai.queryActionIcon('controlpanel', 'uwosh-northstar-app-generator'):
        ai.removeActionIcon('controlpanel', 'uwosh-northstar-app-generator')

def uninstall(context):
    
    if not context.readDataFile('uwosh.northstar-uninstall.txt'):
        return
    
    site = context.getSite()
    cp = getToolByName(site, 'portal_controlpanel')
    cp.unregisterApplication("uwosh.northstar")
    cp.unregisterApplication('uwosh.northstar-app-generator')
    
    remove_action_icons(site)