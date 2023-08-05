# -*- coding: utf-8 -*-

def uninstall(portal, reinstall=False):
    if not reinstall:
        setup_tool = portal.portal_setup
        setup_tool.setBaselineContext('profile-monet.mapsviewlet:uninstall')
        setup_tool.runAllImportStepsFromProfile('profile-monet.mapsviewlet:uninstall')
        

