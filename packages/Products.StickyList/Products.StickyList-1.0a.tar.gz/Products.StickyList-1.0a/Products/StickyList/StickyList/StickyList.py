# -*- coding: utf-8 -*-
#
# File: StickyList.py
#
# Copyright (c) 2009 by Morten W. Petersen
# Generator: ArchGenXML Version 2.0
#            http://plone.org/products/archgenxml
#
# GNU General Public License (GPL)
#

__author__ = """Morten W. Petersen <morten@nidelven-it.no>"""
__docformat__ = 'plaintext'

from AccessControl import ClassSecurityInfo
from Products.Archetypes.atapi import *
from zope.interface import implements
import interfaces

from Products.CMFDynamicViewFTI.browserdefault import BrowserDefaultMixin

from Products.StickyList.config import *

from Products.ATReferenceBrowserWidget.ATReferenceBrowserWidget import ReferenceBrowserWidget

##code-section module-header #fill in your manual code here
##/code-section module-header

schema = Schema((
    ReferenceField('selection_1',
                   relationship = 'relatesTo',
                   multiValued = False,
                    widget = ReferenceBrowserWidget(
    allow_search = True,
    allow_browse = True,
    show_indexes = False,
    force_close_on_insert = True,
    description = '',
    )),
    ReferenceField('selection_2',
                   relationship = 'relatesTo2',
                   multiValued = False,
                    widget = ReferenceBrowserWidget(
    allow_search = True,
    allow_browse = True,
    show_indexes = False,
    force_close_on_insert = True,
    description = '',
    )),
    ReferenceField('selection_3',
                   relationship = 'relatesTo3',
                   multiValued = False,
                    widget = ReferenceBrowserWidget(
    allow_search = True,
    allow_browse = True,
    show_indexes = False,
    force_close_on_insert = True,
    description = '',
    )),
    ReferenceField('selection_4',
                   relationship = 'relatesTo4',
                   multiValued = False,
                    widget = ReferenceBrowserWidget(
    allow_search = True,
    allow_browse = True,
    show_indexes = False,
    force_close_on_insert = True,
    description = '',
    )),
    ReferenceField('selection_5',
                   relationship = 'relatesTo5',
                   multiValued = False,
                    widget = ReferenceBrowserWidget(
    allow_search = True,
    allow_browse = True,
    show_indexes = False,
    force_close_on_insert = True,
    description = '',
    )),
    ReferenceField('selection_6',
                   relationship = 'relatesTo6',
                   multiValued = False,
                    widget = ReferenceBrowserWidget(
    allow_search = True,
    allow_browse = True,
    show_indexes = False,
    force_close_on_insert = True,
    description = '',
    )),
    ReferenceField('selection_7',
                   relationship = 'relatesTo7',
                   multiValued = False,
                    widget = ReferenceBrowserWidget(
    allow_search = True,
    allow_browse = True,
    show_indexes = False,
    force_close_on_insert = True,
    description = '',
    )),
    ReferenceField('selection_8',
                   relationship = 'relatesTo8',
                   multiValued = False,
                    widget = ReferenceBrowserWidget(
    allow_search = True,
    allow_browse = True,
    show_indexes = False,
    force_close_on_insert = True,
    description = '',
    )),
    ReferenceField('selection_9',
                   relationship = 'relatesTo9',
                   multiValued = False,
                    widget = ReferenceBrowserWidget(
    allow_search = True,
    allow_browse = True,
    show_indexes = False,
    force_close_on_insert = True,
    description = '',
    )),
),
)

##code-section after-local-schema #fill in your manual code here
##/code-section after-local-schema

StickyList_schema = BaseSchema.copy() + \
    schema.copy()

##code-section after-schema #fill in your manual code here
##/code-section after-schema

class StickyList(BaseContent, BrowserDefaultMixin):
    """
    """
    security = ClassSecurityInfo()
    implements(interfaces.IStickyList)

    meta_type = 'StickyList'
    _at_rename_after_creation = True

    schema = StickyList_schema

    ##code-section class-header #fill in your manual code here

    def get_items(self):
        """Returns a list with item items."""
        selected = []
        for x in range(1,10):
            selected.append(getattr(self, 'getSelection_' + str(x))())
        selected = filter(None, selected)
        return selected

    ##/code-section class-header

    # Methods

registerType(StickyList, PROJECTNAME)
# end of class StickyList

##code-section module-footer #fill in your manual code here
##/code-section module-footer
