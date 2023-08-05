""" Custom setup
"""
from Products.CMFCore.utils import getToolByName

def importVarious(self):
    if self.readDataFile('eea.tags.txt') is None:
        return

    site = self.getSite()
    setup_tool = getToolByName(site, 'portal_setup')

    # jQuery TokenInput
    setup_tool.setImportContext('profile-eea.jquery:16-tokeninput')
    setup_tool.runAllImportSteps()
