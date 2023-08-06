# -*- coding: utf-8 -*-
#
# File: Radioschedule.py
#
# Copyright (c) 2011 by unknown <unknown>
# Generator: ArchGenXML Version 2.6
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

from Products.ATContentTypes.content.folder import ATFolder
from Products.ATContentTypes.content.folder import ATFolderSchema
from Products.RadioSchedule.config import *
from DateTime import DateTime
from Products.CMFCore.utils import getToolByName

##code-section module-header #fill in your manual code here
##/code-section module-header

schema = Schema((


),
)

##code-section after-local-schema #fill in your manual code here
##/code-section after-local-schema

Radioschedule_schema = ATFolderSchema.copy() + \
    schema.copy()

##code-section after-schema #fill in your manual code here
##/code-section after-schema

class Radioschedule(ATFolder):
    """
    """
    security = ClassSecurityInfo()

    implements(interfaces.IRadioschedule)

    meta_type = 'Radioschedule'
    _at_rename_after_creation = True

    schema = Radioschedule_schema

    ##code-section class-header #fill in your manual code here
    ##/code-section class-header

    # Methods
    def get_selected_days(self, start_day=None):
        brains = []
        selected_days = []
        catalog = getToolByName(self, 'portal_catalog')
        if not start_day:
            start_day = DateTime(DateTime().strftime('%Y.%m.%d 00:00'))
        for x in range(7):
            try:
                brains.append(catalog.searchResults({'start': start_day+x, 'portal_type': 'Day', 
                                                     'review_state': 'external'})[0])
            except IndexError:
                # No published day on that date added
                pass
        for item in brains:
            selected_days.append(item.getObject())
        return selected_days

registerType(Radioschedule, PROJECTNAME)
# end of class Radioschedule

##code-section module-footer #fill in your manual code here
##/code-section module-footer

