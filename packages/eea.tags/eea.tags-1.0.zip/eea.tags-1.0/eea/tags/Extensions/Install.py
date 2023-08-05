# Plone 2.5 compatible
from Products.CMFCore.utils import getToolByName
from zExceptions import NotFound

try:
    import zope.annotation
    zope.annotation
except ImportError:
    #BBB Plone 2.5
    def install(portal):
        setup_tool = getToolByName(portal, 'portal_setup')
        setup_tool.setImportContext('profile-eea.tags:default')
        res = setup_tool.runAllImportSteps()
        messages = res.get('messages', {})
        output = [message for message in messages.values() if message]
        return '\n'.join(output)
else:
    # Plone 3.0+ doesn't need an installation method
    raise NotFound
