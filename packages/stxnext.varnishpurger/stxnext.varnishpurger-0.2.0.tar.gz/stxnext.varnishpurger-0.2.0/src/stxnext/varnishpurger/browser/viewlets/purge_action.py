# -*- coding: utf-8 -*-
import httplib

from AccessControl import Unauthorized
from zope.component import getUtility
from zope.component import getMultiAdapter
from Products.CMFCore.utils import getToolByName
from Products.statusmessages.interfaces import IStatusMessage
from Products.Five import BrowserView
from Products.CMFPlone.interfaces import IPloneSiteRoot

from stxnext.varnishpurger.utils import getUidOrId
from stxnext.varnishpurger import VPMessageFactory as _

class PurgeActionView(BrowserView):
    
    def PurgeAction(self):
        """
        Purging actual object's cache by sending prepared request.
        The example request: 
        PURGE 5bf8c564b5da741f9bc9a14ca2509b94 HTTP/1.1
        Host: localhost:6081
        """
        mtool = getToolByName(self, 'portal_membership')
        host, port = self.getVarnishAddress()
        if not mtool.checkPermission("Modify portal content", self.context):
            raise Unauthorized
        
        purging_uids = [getUidOrId(self.context)]
        context_state = getMultiAdapter((self.context, self.request), name='plone_context_state')
        if context_state.is_default_page():
            purging_uids.append(getUidOrId(context_state.parent()))
        
        #TODO: Handle exceptions of connection problem
        for uid in purging_uids:
            connection = httplib.HTTPConnection(host, port)
            connection.putrequest('PURGE', uid)
            connection.putheader('Host', host + ':' + port)
            connection.endheaders()
            connection.send('')
            response = connection.getresponse()
        
        messages = IStatusMessage(self.request)
        messages.addStatusMessage(_("Cache of the page has been purged"), type="info")
        return self.request.RESPONSE.redirect(self.context.absolute_url())

    def getVarnishAddress(self):
        """
        """
        portal = getUtility(IPloneSiteRoot)
        varnish_host = portal.portal_properties.site_properties.getProperty('varnish_host', '')
        return varnish_host.split(':')
        