# -*- coding: utf-8 -*-

from collective.jqueryui.autocomplete import logger

def uninstall(portal, reinstall=False):
    setup_tool = portal.portal_setup
    setup_tool.setBaselineContext('profile-collective.jqueryui.autocomplete:uninstall')
    setup_tool.runAllImportStepsFromProfile('profile-collective.jqueryui.autocomplete:uninstall')
    logger.info("collective.jqueryui.autocomplete removed")
