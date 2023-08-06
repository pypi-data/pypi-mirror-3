# -*- coding: utf-8 -*-
from Products.CMFCore.utils import getToolByName
from zope.component import getUtility
from zope.component import getMultiAdapter
from zope.component import getSiteManager
from zope.app.component.hooks import getSite
from Products.ATSuccessStory.browser.portlets.successstory import ISuccessStoryPortlet
from plone.portlets.interfaces import IPortletManager
from plone.portlets.interfaces import IPortletAssignmentMapping
from plone.portlets.interfaces import ILocalPortletAssignable
from zLOG import LOG, INFO, WARNING
from Products.ATSuccessStory.config import PROJECTNAME

from plone.portlets.constants import USER_CATEGORY
from plone.portlets.constants import GROUP_CATEGORY
from plone.portlets.constants import CONTENT_TYPE_CATEGORY
from plone.portlets.constants import CONTEXT_CATEGORY

import transaction

def fix_search_path(assignement, site, location):
    # Now we get all Success Story Folders
    ss_portlets = [i for i in assignement.values() if ISuccessStoryPortlet.providedBy(i)]

    try:
        location = '/'.join(location.getPhysicalPath())
    except:
        pass
    
    for portlet in ss_portlets:
        if hasattr(portlet.data, 'global_portlet'):
            
            msg = u"Fixing portlet \"%s\" for %s"%(portlet.header, location)
            LOG(PROJECTNAME, INFO, msg)
            if not portlet.data.global_portlet:
                # If it's not a global portlet, we get the searchpath
                search_path = portlet.searchpath

                msg = u"This is not a global portlet, old search path: %s"%search_path
                LOG(PROJECTNAME, INFO, msg)
                if search_path.startswith('/'):
                    search_path = search_path[1:]

                try:
                    ss_folder = site.unrestrictedTraverse(search_path)
                except:
                    break

            else:

                msg = u"This is a global portlet"
                LOG(PROJECTNAME, INFO, msg)
                # If it is, we just set the searchpath to site root
                ss_folder = site


            search_path = '/'.join(ss_folder.getPhysicalPath())

            msg = u"New search path %s"%search_path
            LOG(PROJECTNAME, INFO, msg)
            portlet.data.searchpath = search_path
            del portlet.data.global_portlet

        else:
            msg = u"Portlet \"%s\" for %s is already updated"%(portlet.header, location)
            LOG(PROJECTNAME, INFO, msg)

def updatePortlets(portal_setup):
    """
    This migration step will search all existing portlets and make the proper
    changes so they keep working
    """

    msg = u"Starting to update portlets"
    LOG(PROJECTNAME, INFO, msg)
    # Part of this code was obtained from plone.app.portlets.test.test_setup.py

    site = getSite()
    pc = getToolByName(site, 'portal_catalog')
    sm = getSiteManager(site)
    
    # This will give me a list with the names of the registered portlet managers
    registrations = [r.name for r in sm.registeredUtilities()
                        if IPortletManager == r.provided]

    # We now get a list of possible local portlet assignment locations
    locations = pc.searchResults(object_provides=ILocalPortletAssignable.__identifier__)
    
    for name in registrations:
        # Now for each manager name, i get the manager
        column = getUtility(IPortletManager, name=name, context=site)

        # Now that i have the manager, i need to go on each possible place
        # where this manager has assigned portlets
        for location in locations:
            place = location.getObject()
        
            assignement = getMultiAdapter((place, column), IPortletAssignmentMapping)
            fix_search_path(assignement, site, place)

        # Now we get the portlets from the global categories
        # This is taken from plone.app.portlets.exportimport.portlets.py
        for category in (USER_CATEGORY, GROUP_CATEGORY, CONTENT_TYPE_CATEGORY, CONTEXT_CATEGORY,):
            for name, assignement in column.get(category, {}).items():
                fix_search_path(assignement, site, category)
                
        # Finally we do the same for the site root
        assignement = getMultiAdapter((site, column), IPortletAssignmentMapping)
        fix_search_path(assignement, site, site)

    transaction.savepoint()