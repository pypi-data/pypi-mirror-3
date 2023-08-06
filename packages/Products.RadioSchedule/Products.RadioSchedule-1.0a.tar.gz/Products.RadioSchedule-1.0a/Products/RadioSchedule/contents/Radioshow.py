# -*- coding: utf-8 -*-
#
# File: Radioshow.py
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

from Products.ATContentTypes.content.document import ATDocument
from Products.ATContentTypes.content.document import ATDocumentSchema
from Products.RadioSchedule.config import *

from Acquisition import aq_inner, aq_parent
import pdb

##code-section module-header #fill in your manual code here
##/code-section module-header

schema = Schema((

    StringField(
        name='name',
        required=1,
        widget=StringField._properties['widget'](
            label='Name',
            label_msgid='RadioSchedule_label_name',
            i18n_domain='RadioSchedule',
        ),
    ),
    StringField(
        name='start_time',
        required=1,
        validators=('isTime'),
        widget=StringField._properties['widget'](
            size=5,
            label='Start time',
            description='Use the format hh:mm',
            label_msgid='RadioSchedule_label_start_time',
            description_msgid='RadioSchedule_description_end_time',
            i18n_domain='RadioSchedule',
        ),
    ),
    StringField(
        name='end_time',
        required=1,
        validators=('isEndTime'),
        widget=StringField._properties['widget'](
            size=5,
            label='End time',
            description='Use the format hh:mm',
            label_msgid='RadioSchedule_label_end_time',
            description_msgid='RadioSchedule_description_end_time',
            i18n_domain='RadioSchedule',
        ),
    ),
    ComputedField(
        name='sortable_time',
        expression='context.get_sortable_time()',
        widget=ComputedWidget(
            label='Sortable time',
            label_msgid='RadioSchedule_label_sortable_time',
            i18n_domain='RadioSchedule',
        ),
    ),
),
)

##code-section after-local-schema #fill in your manual code here
##/code-section after-local-schema

Radioshow_schema = schema.copy() + ATDocumentSchema.copy()

##code-section after-schema #fill in your manual code here
Radioshow_schema["title"].required = 0
Radioshow_schema["title"].widget.visible = {"edit": "invisible", "view": "invisible"}
Radioshow_schema["text"].widget.visible = {"edit": "invisible", "view": "invisible"}
#FIXME - where does this belong?
#Radioshow_schema["sound"].widget.visible = {"edit": "invisible", "view": "invisible"}
Radioshow_schema["presentation"].widget.visible = {"edit": "invisible", "view": "invisible"}
Radioshow_schema["tableContents"].widget.visible = {"edit": "invisible", "view": "invisible"}

from ExcludeFromNavMixin import ExcludeFromNavMixin
##/code-section after-schema

class Radioshow(ExcludeFromNavMixin, ATDocument):
    """
    """
    security = ClassSecurityInfo()

    implements(interfaces.IRadioshow)

    meta_type = 'Radioshow'
    _at_rename_after_creation = True
    
    exclude_from_nav = True

    schema = Radioshow_schema

    ##code-section class-header #fill in your manual code here
    def setName(self, value):
        self.Schema()['name'].set(self, value)
        self.setTitle(value)

    ##/code-section class-header

    # Methods
    def get_sortable_time(self):
        return int(self.start_time.replace(':', ''))


registerType(Radioshow, PROJECTNAME)
# end of class Radioshow

##code-section module-footer #fill in your manual code here
##/code-section module-footer

