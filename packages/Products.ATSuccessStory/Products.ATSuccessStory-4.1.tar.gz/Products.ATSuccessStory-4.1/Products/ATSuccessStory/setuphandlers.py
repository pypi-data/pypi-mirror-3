# -*- coding: utf-8 -*-
#
# File: setuphandlers.py
#
# Copyright (c) 2008 by []
# Generator: ArchGenXML Version 2.1
#            http://plone.org/products/archgenxml
#
# GNU General Public License (GPL)
#

__author__ = """Franco Pellegrini <frapell@menttes.com>"""
__docformat__ = 'plaintext'


import logging
logger = logging.getLogger('ATSuccessStory: setuphandlers')
from Products.ATSuccessStory.config import PROJECTNAME
from Products.ATSuccessStory.config import DEPENDENCIES
import os
from Products.CMFCore.utils import getToolByName
import transaction
##code-section HEAD
##/code-section HEAD

def isNotATSuccessStoryProfile(context):
    return context.readDataFile("ATSuccessStory_marker.txt") is None



def updateRoleMappings(context):
    """after workflow changed update the roles mapping. this is like pressing
    the button 'Update Security Setting' and portal_workflow"""
    if isNotATSuccessStoryProfile(context): return 
    wft = getToolByName(context.getSite(), 'portal_workflow')
    wft.updateRoleMappings()


def postInstall(context):
    """Called as at the end of the setup process. """
    # the right place for your custom code
    if isNotATSuccessStoryProfile(context): return 
    site = context.getSite()


##code-section FOOT
##/code-section FOOT
