# -*- coding: utf-8 -*-

# Zope imports
from zope.interface import implements
from AccessControl import ClassSecurityInfo

# CMF imports
from Products.CMFCore import permissions as CCP

from Products.Archetypes.public import *

# Products imports
from Products.ATContentTypes.content.base import ATCTOrderedFolder
from Products.ATContentTypes.content.schemata import ATContentTypeSchema
from Products.ATContentTypes.content.schemata import NextPreviousAwareSchema
from Products.ATContentTypes.lib.constraintypes import ConstrainTypesMixinSchema

from collective.phantasy.atphantasy.interfaces import IPhantasySkinsRepository
from collective.phantasy.config import PROJECTNAME


StandardFolderSchema =  ATContentTypeSchema.copy() + ConstrainTypesMixinSchema + NextPreviousAwareSchema

PhantasySkinsRepositorySchema = StandardFolderSchema.copy()

class PhantasySkinsRepository(ATCTOrderedFolder):
    """Phantasy Skin folder"""

    portal_type = meta_type = 'PhantasySkinsRepository'
    archetype_name = 'Phantasy Skins Repository'
    global_allow = True
    filter_content_types = True
    allowed_content_types = ('PhantasySkin',)
    schema = PhantasySkinsRepositorySchema
    implements(IPhantasySkinsRepository)


    security       = ClassSecurityInfo()

    security.declareProtected(CCP.View, 'getNextPreviousParentValue')
    def getNextPreviousParentValue(self):
        """
        """
        parent = self.getParentNode()
        from Products.ATContentTypes.interface.folder import IATFolder as IATFolder_
        if IATFolder_.providedBy(parent):
            return parent.getNextPreviousEnabled()
        else:
            return False

    def manage_afterAdd(self, item, container):
        ATCTOrderedFolder.manage_afterAdd(self, item, container)


    security.declarePrivate('initializeArchetype')
    def initializeArchetype(self, **kwargs):
        ATCTOrderedFolder.initializeArchetype(self, **kwargs)
        # we do not want Language attributes
        self.setLanguage('')


registerType(PhantasySkinsRepository, PROJECTNAME)
