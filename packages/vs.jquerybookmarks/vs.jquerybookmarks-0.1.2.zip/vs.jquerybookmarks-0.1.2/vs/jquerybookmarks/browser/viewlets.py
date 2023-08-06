from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from plone.app.layout.viewlets.common import ViewletBase
from Products.CMFCore.utils import getToolByName

class MyViewlet(ViewletBase):
    render = ViewPageTemplateFile('viewlet.pt')

    def available(self):
        qi = getToolByName(self.context, 'portal_quickinstaller')
        ids = [p['id'] for p in qi.listInstalledProducts()]
        return 'vs.jquerybookmarks' in ids

