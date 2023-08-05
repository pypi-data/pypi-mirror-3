# -*- coding: utf-8 -*-
from zope.component import getSiteManager
import logging

logger = logging.getLogger('collective.perseoschema')

def removeBrowserLayer(site):
    """ Remove collective.perseo.schema.org browser layer.
    """
    from plone.browserlayer.utils import unregister_layer
    from plone.browserlayer.interfaces import ILocalBrowserLayerType

    name = "collective.perseo.schema.org"
    site = getSiteManager(site)
    registeredLayers = [r.name for r in site.registeredUtilities()
                        if r.provided == ILocalBrowserLayerType]
    if name in registeredLayers:
        unregister_layer(name, site_manager=site)
        logger.log(logging.INFO, "Unregistered \"%s\" browser layer." % name)

def install(portal):
    setup_tool = portal.portal_setup
    setup_tool.setBaselineContext('profile-collective.perseoschema:default')
    setup_tool.runAllImportStepsFromProfile('profile-collective.perseoschema:default')

def uninstall(portal):
    setup_tool = portal.portal_setup
    setup_tool.setBaselineContext('profile-collective.perseoschema:uninstall')
    setup_tool.runAllImportStepsFromProfile('profile-collective.perseoschema:uninstall')
    removeBrowserLayer(portal)
