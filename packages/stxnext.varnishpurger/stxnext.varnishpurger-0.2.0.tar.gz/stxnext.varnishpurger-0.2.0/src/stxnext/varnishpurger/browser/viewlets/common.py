# -*- coding: utf-8 -*-
from plone.app.layout.viewlets.common import ViewletBase
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from Products.CMFCore.utils import getToolByName


class VarnishPurgeViewlet(ViewletBase):
    """
    Viewlet displaing link to purge
    actual url from varnish cache
    """
    
    render = ViewPageTemplateFile('varnish_purge.pt')
    
    def showPurgeViewlet(self):
        """
        Returns boolean information if
        the purge viewlet should be displayed 
        """
        mtool = getToolByName(self.context, "portal_membership")
        if mtool.checkPermission("Modify portal content", self.context):
            return True
        return False
