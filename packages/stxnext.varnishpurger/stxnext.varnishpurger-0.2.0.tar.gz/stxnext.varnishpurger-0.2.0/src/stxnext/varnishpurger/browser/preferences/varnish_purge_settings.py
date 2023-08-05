# -*- coding: utf-8 -*-
from zope import interface
from zope.component import adapts
from zope.formlib.form import Fields, FormFields
from zope.interface import implements
from zope.schema import TextLine, Text

from Products.CMFDefault.formlib.schema import SchemaAdapterBase, ProxyFieldProperty
from Products.CMFPlone.interfaces import IPloneSiteRoot
from plone.app.controlpanel.site import SiteControlPanel, SiteControlPanelAdapter, ISiteSchema
from plone.app.controlpanel.form import ControlPanelForm

from stxnext.varnishpurger import VPMessageFactory as _

class IVarnishPurgerSettingsSchema(interface.Interface):
    """
    Interface for additional fields in Site Control Panel
    """
    varnish_host = TextLine(title=_(u'Varnish host'),
                           description=_(u"Varnish host address in format: hostname:port_number"),
                           default=u'localhost:6081',
                           required=False)

class VarnishPurgerSettingsControlPanelAdapter(SiteControlPanelAdapter):
    """Adapter required for control-panel."""
    adapts(IPloneSiteRoot)
    implements(IVarnishPurgerSettingsSchema)

    varnish_host = ProxyFieldProperty(IVarnishPurgerSettingsSchema['varnish_host'])

class VarnishPurgerSettingsForm(ControlPanelForm):
    """Static export form"""
    
    form_fields = FormFields(IVarnishPurgerSettingsSchema)

    label = _("Varnish cache purging settings")
    description = None
    form_name = _("Varnish cache purging settings")
