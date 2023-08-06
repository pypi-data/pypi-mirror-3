# -*- coding: utf-8 -*-
#
# File: ForumPage.py
#
# Copyright (c) 2008 by 
# Generator: ArchGenXML Version 2.0
#            http://plone.org/products/archgenxml
#
# GNU General Public License (GPL)
#

__author__ = """unknown <unknown>"""
__docformat__ = 'plaintext'

from AccessControl import ClassSecurityInfo
from Products.Archetypes.atapi import *
from zope.interface import implements
import interfaces

from Products.CMFDynamicViewFTI.browserdefault import BrowserDefaultMixin

from Products.ATReferenceBrowserWidget.ATReferenceBrowserWidget import ReferenceBrowserWidget
from Products.ATContentTypes import ATCTMessageFactory as _


from Products.ForumPage.config import *
from Products.CMFCore.utils import getToolByName

from DateTime import DateTime

##code-section module-header #fill in your manual code here
##/code-section module-header

schema = Schema((
    ReferenceField('primary_forum_item',
                   allowed_types=('PloneboardForum',),
                   relationship = 'relatesTo',
                   multiValued = False,
                   widget = ReferenceBrowserWidget(
         allow_search = True,
         allow_browse = False,
         show_indexes = False,
         show_path = True,
         show_results_without_query = True,
         force_close_on_insert = True,
         label = _(u'primary_forum_item', default=u'1. Forum'),
         description = '',
         )),
    ReferenceField('secondary_forum_item',
                   allowed_types=('PloneboardForum',),
                   relationship = 'relatesTo2',
                   multiValued = False,
                   widget = ReferenceBrowserWidget(
         allow_search = True,
         allow_browse = True,
         show_indexes = False,
         show_path = True,
         show_results_without_query = True,
         force_close_on_insert = True,
         label = _(u'primary_forum_item', default=u'2. Forum'),
         description = '',
         )),    
    ReferenceField('tertiary_forum_item',
                   allowed_types=('PloneboardForum',),
                   relationship = 'relatesTo3',
                   multiValued = False,
                   widget = ReferenceBrowserWidget(
         allow_search = True,
         allow_browse = True,
         show_indexes = False,
         show_path = True,
         show_results_without_query = True,
         force_close_on_insert = True,
         label = _(u'primary_forum_item', default=u'3. Forum'),
         description = '',
         )),
    IntegerField('number_of_posts_per_forum', default=3),
),
)

##code-section after-local-schema #fill in your manual code here
##/code-section after-local-schema

ForumPage_schema = BaseSchema.copy() + \
    schema.copy()

##code-section after-schema #fill in your manual code here
##/code-section after-schema

# Ploneboard code
from plone.i18n.normalizer.interfaces import IIDNormalizer
from zope.component import getUtility
from zope.component import getMultiAdapter

# Own utilities

import utilities

class ForumPage(BaseContent, BrowserDefaultMixin):
    """
    """
    security = ClassSecurityInfo()
    implements(interfaces.IForumPage)

    meta_type = 'ForumPage'
    _at_rename_after_creation = True

    schema = ForumPage_schema

    ##code-section class-header #fill in your manual code here
    exclude_from_nav = True    
    ##/code-section class-header

    # Methods

    def check_b_start(self, b_start):
        if b_start == 0:
            return 1

    def get_board_items(self):
        """Returns a list with forum item forumitems."""
        objects = [self.getPrimary_forum_item(), self.getSecondary_forum_item(), self.getTertiary_forum_item()]
        objects = filter(None, objects)
        return objects

    def primary_forums(self):
        """Returns the top 3 forum item objects."""
        objects = []
        brains = self.get_board_items()
        for brain in brains[:3]:
            objects.append(brain)
        return objects

    def secondary_forums(self):
        """Returns rest of the forum."""
        objects = []
        brains = self.get_forum_items()
        for brain in brains[3:]:
            objects.append(brain)
        return objects

# Following bulk of code shamelessly stolen from Ploneboard and modified

    def get_forum_postings(self, forum):
        "Gets forum postings from given forum."
        count = self.getNumber_of_posts_per_forum()
        ct=getToolByName(self, "portal_catalog")
        normalize=getUtility(IIDNormalizer).normalize
        brains=ct(
                object_provides="Products.Ploneboard.interfaces.IConversation",
                sort_on="modified",
                sort_order="reverse",
                sort_limit=count,
                path='/'.join(forum.getPhysicalPath())
        )[:count]

        def morph(brain):
            obj=brain.getObject()
            comment = obj.getComments(limit=1)[0].getText()
            comment = utilities.render_html_as_text(comment, size=50, format_newlines_as_html=True)
            return dict(
                        title = brain.Title,
                        description = brain.Description,
                        url = brain.getURL()+"/view",
                        review_state = normalize(brain.review_state),
                        portal_type = normalize(brain.portal_type),
                        date = brain.modified,
                        object = obj,
                        creator = brain.Creator,
                        comment = comment
                        )

        list = []
        for brain in brains:
           conversation = morph(brain)
           if conversation is not None:
               list.append(conversation)
        return list


registerType(ForumPage, PROJECTNAME)
# end of class ForumPage

##code-section module-footer #fill in your manual code here
##/code-section module-footer



