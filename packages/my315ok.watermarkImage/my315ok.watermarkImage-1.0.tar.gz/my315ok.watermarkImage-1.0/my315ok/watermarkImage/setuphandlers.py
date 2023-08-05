from Products.CMFCore.utils import getToolByName

def removeConfiglet(self):
    if self.readDataFile('sitewatermark-uninstall.txt') is None:
        return
    portal_conf=getToolByName(self.getSite(),'portal_controlpanel')
    portal_conf.unregisterConfiglet('PloneAppSiteWatermark')
