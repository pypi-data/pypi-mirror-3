from raptus.article.multilanguagefields import modifier

from Products.CMFCore.utils import getToolByName

modifiers = [modifier.ArticleModifier,
             modifier.TeaserModifier,
             modifier.AdditionalwysiwygModifier,
             modifier.MapsModifier,
             modifier.MarkerModifier,
             modifier.CollectionModifier]

def install(context):

    if context.readDataFile('raptus.article.multilanguagefields_install.txt') is None:
        return
    
    portal = context.getSite()
    quickinstaller = getToolByName(portal, 'portal_quickinstaller')

    sm = portal.getSiteManager()
    for modifier in modifiers:
        if quickinstaller.isProductInstalled(modifier.for_package):
            sm.unregisterAdapter(modifier, name='MultilanguageArticle%s' % modifier.__name__)
            sm.registerAdapter(modifier, name='MultilanguageArticle%s' % modifier.__name__)

def uninstall(context):
    if context.readDataFile('raptus.article.multilanguagefields_uninstall.txt') is None:
        return
    
    portal = context.getSite()
    sm = portal.getSiteManager()
    for modifier in modifiers:
        sm.unregisterAdapter(modifier, name='MultilanguageArticle%s' % modifier.__name__)
