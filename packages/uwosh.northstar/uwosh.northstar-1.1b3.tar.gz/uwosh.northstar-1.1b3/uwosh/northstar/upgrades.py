from Products.CMFCore.utils import getToolByName

from setupHandlers import remove_action_icons
default_profile = 'profile-uwosh.northstar:default'
uninstall_profile = 'profile-uwosh.northstar:uninstall'

def upgrade_to_0_3(context):
    context.runImportStepFromProfile(default_profile, 'action-icons')
    
def upgrade_to_0_5b1(context):
    context.runImportStepFromProfile(default_profile, 'controlpanel')
    context.runImportStepFromProfile(default_profile, 'action-icons')
    
    
def upgrade_to_0_8rc1(context):
    context.runImportStepFromProfile(default_profile, 'controlpanel')
    
text_replace_mapping = {
    'object_url' : "url",
    'portal_url' : "absolute_url",
    'object_title' : "title",
    'member_fullname' : "user_fullname",
    'previous_state' : "review_state",
    'transition' : "review_title",
    'site_owner_email' : "owner_emails",
    'authenticated_user_email' : "user_email"
}
    
def mailer_text_replacements(val):
    for k, v in text_replace_mapping.items():
        val = val.replace("{{" + k + "}}", "${" + v + "}")
    return val
    
def upgrade_to_0_9b1(context):
    site = getToolByName(context, 'portal_url').getPortalObject()
    remove_action_icons(context)
    context.runImportStepFromProfile(default_profile, 'controlpanel')
    
                
def upgrade_to_1_1(context):
    cp = getToolByName(context, 'portal_controlpanel')
    cp.unregisterConfiglet('uwosh-northstar')
    qi = getToolByName(context, 'portal_quickinstaller')
    if not qi.isProductInstalled('plone.app.workflowmanager'):
        qi.installProducts(['plone.app.workflowmanager'])
    