# -*- coding: utf-8 -*-
#
# File: Week.py
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

##code-section module-header #fill in your manual code here
from DateTime import DateTime
##/code-section module-header

schema = Schema((

    DateTimeField(
        name='dateofweek',
        widget=DateTimeField._properties['widget'](
            format='%d.%m.%Y',
            starting_year= '2011',
            show_hm=False,
            label='Date',
            label_msgid='RadioSchedule_label_dateofweek',
            i18n_domain='RadioSchedule',
        ),
    ),

),
)

##code-section after-local-schema #fill in your manual code here
##/code-section after-local-schema

Week_schema = ATFolderSchema.copy() + \
    schema.copy()

##code-section after-schema #fill in your manual code here
Week_schema["title"].required = 0
Week_schema["title"].widget.visible = {"edit": "invisible", "view": "invisible"}
Week_schema["description"].widget.visible = {"edit": "invisible", "view": "invisible"}

from ExcludeFromNavMixin import ExcludeFromNavMixin
##/code-section after-schema

class Week(ExcludeFromNavMixin, ATFolder):
    """
    """
    security = ClassSecurityInfo()

    implements(interfaces.IWeek)

    meta_type = 'Week'
    _at_rename_after_creation = True

    exclude_from_nav = True

    schema = Week_schema

    ##code-section class-header #fill in your manual code here
    def getWeek(self):
        return self

    def Title(self):
        dateofweek = self.getDateofweek()
        if dateofweek is not None:
            return "Uke " + str(dateofweek.week())
        else:
            return "Uke ?"

    def getStartingDate(self):
        dateofweek = self.getDateofweek()
        day = dateofweek.dow()
        dateofweek = dateofweek - day
        dateofweek = DateTime(dateofweek.strftime('%Y.%m.%d 00:00'))
        return dateofweek

    def getWeekAsDate(self):
        return self.getDateofweek()

#    def manage_afterAdd(self, item, container):
#        weekdays = ["Mandag", "Tirsdag", "Onsdag", "Torsdag", "Fredag", "L\xc3\xb8rdag", "S\xc3\xb8ndag"]
#        for day in weekdays:
#            self.invokeFactory('day', day, title=day)

    # Methods

registerType(Week, PROJECTNAME)
# end of class Week

##code-section module-footer #fill in your manual code here
##/code-section module-footer

