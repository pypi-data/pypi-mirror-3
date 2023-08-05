# -*- coding: utf-8 -*-

def uninstall(portal, reinstall=False):
    setup_tool = portal.portal_setup
    setup_tool.setBaselineContext('profile-collective.flowplayer_toolbar:uninstall')
    setup_tool.runAllImportStepsFromProfile('profile-collective.flowplayer_toolbar:uninstall')

