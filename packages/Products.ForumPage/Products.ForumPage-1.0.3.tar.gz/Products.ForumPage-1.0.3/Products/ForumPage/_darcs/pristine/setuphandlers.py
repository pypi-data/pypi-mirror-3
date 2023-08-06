# -*- coding: utf-8 -*-
#
# File: setuphandlers.py
#
# Copyright (c) 2008 by 
# Generator: ArchGenXML Version 2.0
#            http://plone.org/products/archgenxml
#
# GNU General Public License (GPL)
#

__author__ = """unknown <unknown>"""
__docformat__ = 'plaintext'


import logging
logger = logging.getLogger('ForumPage: setuphandlers')
from Products.ForumPage.config import PROJECTNAME
from Products.ForumPage.config import DEPENDENCIES
import os
from Products.CMFCore.utils import getToolByName
import transaction
##code-section HEAD
##/code-section HEAD

def isNotForumPageProfile(context):
    return context.readDataFile("ForumPage_marker.txt") is None



def updateRoleMappings(context):
    """after workflow changed update the roles mapping. this is like pressing
    the button 'Update Security Setting' and portal_workflow"""
    if isNotForumPageProfile(context): return 
    shortContext = context._profile_path.split(os.path.sep)[-3]
    if shortContext != 'ForumPage': # avoid infinite recursions
        return
    wft = getToolByName(context.getSite(), 'portal_workflow')
    wft.updateRoleMappings()


def postInstall(context):
    """Called as at the end of the setup process. """
    # the right place for your custom code
    if isNotForumPageProfile(context): return 
    shortContext = context._profile_path.split(os.path.sep)[-3]
    if shortContext != 'ForumPage': # avoid infinite recursions
        return
    site = context.getSite()


##code-section FOOT
##/code-section FOOT
