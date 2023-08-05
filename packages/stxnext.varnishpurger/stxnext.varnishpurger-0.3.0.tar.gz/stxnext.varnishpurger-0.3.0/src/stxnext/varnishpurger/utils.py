# -*- coding: utf-8 -*-
import os

from ZPublisher.HTTPRequest import BaseRequest
from zope.publisher.browser import BrowserView
from Products.CMFCore.FSPageTemplate import FSPageTemplate
from Products.PythonScripts.PythonScript import PythonScript
from Products.Archetypes.interfaces import IBaseObject
from Products.CMFPlone.Portal import PloneSite

originalTraverse = BaseRequest.traverse

def wrappedTraverse(self, path, response=None, validated_hook=None):
    """
    """
    traverse = originalTraverse(self, path, response, validated_hook)

    extentions = ('.jpg', '.gif', '.png', '.js', '.class', '.css')
    
    if isinstance(traverse, (BrowserView, FSPageTemplate, PythonScript)):
        obj = traverse.aq_parent
    else:
        obj = traverse

    if os.path.splitext(path)[-1].lower() not in extentions and IBaseObject.providedBy(obj) or isinstance(obj, PloneSite):
        self.response.setHeader('X-Context-Uid', getUidOrId(obj))
    return traverse

def installWrapper():
    """
    """
    BaseRequest.traverse = wrappedTraverse
    
def getUidOrId(obj):
    """
    """
    return getattr(obj, 'UID', getattr(obj, 'getId'))()