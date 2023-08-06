# -*- coding: utf-8 -*-
##
## Copyright (C) 2007 Ingeniweb

## This program is free software; you can redistribute it and/or modify
## it under the terms of the GNU General Public License as published by
## the Free Software Foundation; either version 2 of the License, or
## (at your option) any later version.

## This program is distributed in the hope that it will be useful,
## but WITHOUT ANY WARRANTY; without even the implied warranty of
## MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
## GNU General Public License for more details.

## You should have received a copy of the GNU General Public License
## along with this program; see the file LICENSE. If not, write to the
## Free Software Foundation, Inc., 675 Mass Ave, Cambridge, MA 02139, USA.

# $Id: PloneGlossaryDefinition.py 247811 2012-01-14 18:23:59Z naro $
"""
Glossary definition content type
"""
__author__ = ''
__docformat__ = 'restructuredtext'

# Python imports
from AccessControl import ClassSecurityInfo
from zope.interface import implements
# CMF imports
from Products.CMFCore import permissions

# Plone imports
from Products.CMFPlone.utils import getToolByName

# Archetypes imports
try:
    from Products.LinguaPlone.public import registerType
    registerType  # pyflakes
except ImportError:
    # No multilingual support
    from Products.Archetypes.atapi import registerType

from Products.ATContentTypes.content.base import ATCTContent

# Products imports
from Products.PloneGlossary.config import PROJECTNAME
from Products.PloneGlossary.content.schemata import \
    PloneGlossaryDefinitionSchema as schema
from Products.PloneGlossary.utils import html2text
from Products.PloneGlossary.interfaces import IPloneGlossaryDefinition


class PloneGlossaryDefinition(ATCTContent):
    """PloneGlossary definition """
    implements(IPloneGlossaryDefinition)

    schema = schema
    _at_rename_after_creation = True

    security = ClassSecurityInfo()

    security.declareProtected(permissions.View, 'Description')
    def Description(self, from_catalog=False):
        """Returns cleaned text"""

        if from_catalog:
            cat = self.getCatalog()
            brains = cat.searchResults(id=self.getId())

            if not brains:
                return self.Description()

            brain = brains[0]
            return brain.Description
        else:
            html = self.getDefinition()
            return html2text(html)

    security.declareProtected(permissions.ModifyPortalContent, 'indexObject')
    def indexObject(self):
        """Index object in portal catalog and glossary catalog"""
        cat = getToolByName(self, 'portal_catalog')
        cat.indexObject(self)
        cat = self.getCatalog()
        cat.indexObject(self)

    security.declareProtected(permissions.ModifyPortalContent, 'unindexObject')
    def unindexObject(self):
        """Unindex object in portal catalog and glossary catalog"""
        cat = getToolByName(self, 'portal_catalog')
        cat.unindexObject(self)
        cat = self.getCatalog()
        cat.unindexObject(self)

    security.declareProtected(permissions.ModifyPortalContent, 'reindexObject')
    def reindexObject(self, idxs=[]):
        """Reindex object in portal catalog and glossary catalog"""
        cat = getToolByName(self, 'portal_catalog')
        cat.reindexObject(self, idxs)
        cat = self.getCatalog()
        cat.reindexObject(self, idxs)

registerType(PloneGlossaryDefinition, PROJECTNAME)
