from raptus.multilanguagepfg import extender
from raptus.multilanguagepfg import config

from Products.CMFCore.utils import getToolByName

extenders = [extender.FormFolderExtender,
             extender.BaseFormFieldExtender,
             extender.ThanksPageExtender,
             extender.FGLikertFieldExtender,
             extender.FieldsetFolderExtender]

def install(context):

    if context.readDataFile('raptus.multilanguagepfg_install.txt') is None:
        return
    
    portal = context.getSite()
    quickinstaller = getToolByName(portal, 'portal_quickinstaller')

    sm = portal.getSiteManager()
    for extender in extenders:
        sm.unregisterAdapter(extender, name=config.PROJECT_NAME + extender.__name__)
        sm.registerAdapter(extender, name=config.PROJECT_NAME + extender.__name__)

def uninstall(context):
    if context.readDataFile('raptus.multilanguagepfg_uninstall.txt') is None:
        return
    
    portal = context.getSite()
    sm = portal.getSiteManager()
    for extender in extenders:
        sm.unregisterAdapter(extender, name=config.PROJECT_NAME + extender.__name__)
