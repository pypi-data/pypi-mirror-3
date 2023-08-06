# -*- coding: utf-8 -*-
#
# File: Day.py
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
from Products.CMFCore.utils import getToolByName
import pdb

from DateTime import DateTime

##code-section module-header #fill in your manual code here
##/code-section module-header

schema = Schema((

    IntegerField(
        name='weekday',
        required=1,
        default=0,
        vocabulary='get_day_vocabulary',
        widget=SelectionWidget(
            label='Weekday',
            label_msgid='RadioSchedule_label_weekday',
            i18n_domain='RadioSchedule',
        ),
    ),
),
)

##code-section after-local-schema #fill in your manual code here
##/code-section after-local-schema

Day_schema = ATFolderSchema.copy() + \
    schema.copy()

##code-section after-schema #fill in your manual code here
Day_schema["title"].required = 0
Day_schema["title"].widget.visible = {"edit": "invisible", "view": "visible"}
Day_schema["description"].widget.visible = {"edit": "invisible", "view": "invisible"}

from ExcludeFromNavMixin import ExcludeFromNavMixin
##/code-section after-schema

class Day(ExcludeFromNavMixin, ATFolder):
    """
    """
    security = ClassSecurityInfo()

    implements(interfaces.IDay)

    meta_type = 'Day'
    _at_rename_after_creation = True

    exclude_from_nav = True

    schema = Day_schema

    day_vocabulary = (
            (0, "S\xc3\xb8ndag"),
            (1, "Mandag"),
            (2, "Tirsdag",),
            (3, "Onsdag",),
            (4, "Torsdag",),
            (5, "Fredag",),
            (6, "L\xc3\xb8rdag",),
    )

    ##code-section class-header #fill in your manual code here
    def get_day_vocabulary(self):
        return Vocabulary(DisplayList(self.day_vocabulary), self, 'RadioSchedule')

    def Title(self):
        weekday = self.getWeekday()
        for day, name in self.day_vocabulary:
            if day == weekday: return name


    def get_start_date(self):
        week_start = self.getStartingDate()
        try:
            start = week_start + self.getWeekday()
        except TypeError:
            raise str((week_start, self.getWeekday()))
        start = DateTime(start.strftime('%Y.%m.%d 00:00')) 
        return start

    def get_end_date(self):
        return DateTime(self.get_start_date().strftime("%Y.%m.%d 23:59:59"))

    start = get_start_date
    end = get_end_date
    ##/code-section class-header

    # Methods
    def get_radioshows(self):
        query = {}
        objects = []
        catalog = getToolByName(self, 'portal_catalog')
        query['Type'] = 'Radioshow'
        query['path'] = '/'.join(self.getPhysicalPath())
        query['review_state'] = 'external'
        results = catalog.searchResults(**query)
        for brain in results:
            objects.append(brain.getObject())
        return sorted(objects, key=lambda radioshow: radioshow.getSortable_time())


registerType(Day, PROJECTNAME)
# end of class Day

##code-section module-footer #fill in your manual code here
##/code-section module-footer

