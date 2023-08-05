# -*- coding: utf-8 -*-


from zope.interface import implements
from DateTime import DateTime
from AccessControl import ClassSecurityInfo
from App.Common import rfc1123_date

from Products.CMFCore import permissions
from Products.Archetypes.public import *
from Products.ATContentTypes.content.image import ATImage
from Products.ATContentTypes.content.image import ATImageSchema
from collective.phantasy.atphantasy.interfaces import IPhantasySkinImage
from collective.phantasy.config import PROJECTNAME

from AccessControl import Unauthorized
from ZODB.POSException import ConflictError
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone import PloneMessageFactory as _
from Products.CMFPlone.utils import base_hasattr

PhantasySkinImageSchema = ATImageSchema.copy()
PhantasySkinImageSchema['description'].widget.visible = {'view':'invisible',
                                                         'edit':'invisible'}

class PhantasySkinImage(ATImage):
    """Phantasy Skin Image for Collective Phantasy"""

    schema = PhantasySkinImageSchema
    security = ClassSecurityInfo()
    implements(IPhantasySkinImage)
    portal_type = meta_type = 'PhantasySkinImage'
    archetype_name = 'Phantasy Skin Image'
    global_allow = False

    security.declarePrivate('initializeArchetype')
    def initializeArchetype(self, **kwargs):
        ATImage.initializeArchetype(self, **kwargs)
        # we do not want Language attributes for skinimage
        self.setLanguage('')

    security.declareProtected(permissions.View, 'index_html')
    def index_html(self, REQUEST=None, RESPONSE=None):
        """Make it directly viewable when entering the objects URL
        """
        duration = 20
        seconds = float(duration)*24.0*3600.0
        RESPONSE.setHeader('Expires',
                            rfc1123_date((DateTime() + duration).timeTime()))
        RESPONSE.setHeader('Cache-Control',
                           'max-age=%d' % int(seconds))
        return ATImage.index_html(self, REQUEST, RESPONSE)
        
    security.declareProtected(permissions.View, 'check_id')
    def check_id(self, id=None, required=0, alternative_id=None, contained_by=None) :
        """
        we want to allow skin overloads
        """
        # if an alternative id has been supplied, see if we need to use it
        
        if alternative_id and not id:
            id = alternative_id
        
        # make sure we have an id if one is required
        
        if not id:
            if required:
                return _(u'Please enter a name.')
        
            # Id is not required and no alternative was specified, so assume the
            # object's id will be context.getId(). We still should check to make sure
            # context.getId() is OK to handle the case of pre-created objects
            # constructed via portal_factory.  The main potential problem is an id
            # collision, e.g. if portal_factory autogenerates an id that already exists.
        
            id = self.getId()
        
        # do basic id validation
        
        # check for reserved names
        if id in [ 'login', 'layout' ]:
            return _(u'${name} is reserved.', mapping={u'name' : id})
        
        # check for bad characters
        plone_utils = getToolByName(self, 'plone_utils', None)
        if plone_utils is not None:
            bad_chars = plone_utils.bad_chars(id)
            if len(bad_chars) > 0:
                return _(u'${name} is not a legal name. The following characters are invalid: ${characters}',
                         mapping={u'name' : id, u'characters' : ''.join(bad_chars)})
        
        # check for a catalog index
        portal_catalog = getToolByName(self, 'portal_catalog', None)
        if portal_catalog is not None:
            try:
                if id in portal_catalog.indexes() + portal_catalog.schema():
                    return _(u'${name} is reserved.', mapping={u'name' : id})
            except Unauthorized:
                pass # ignore if we don't have permission; will get picked up at the end
        
        # id is good; decide if we should check for id collisions
        portal_factory = getToolByName(self, 'portal_factory', None)
        if contained_by is not None:
            # always check for collisions if a container was passed
            checkForCollision = True
        elif portal_factory is not None and portal_factory.isTemporary(self):
            # always check for collisions if we are creating a new object
            checkForCollision = True
            try:
                # XXX this can't really be necessary, can it!?
                contained_by = self.aq_inner.aq_parent.aq_parent.aq_parent
            except Unauthorized:
                pass
        else:
            # if we have an existing object, only check for collisions if we are
            # changing the id
            checkForCollision = (self.getId() != id)
        
        # check for id collisions
        if checkForCollision:
            # handles two use cases:
            # 1. object has not yet been created and we don't know where it will be
            # 2. object has been created and checking validity of id within container
            if contained_by is None:
                try:
                    contained_by = self.getParentNode()
                except Unauthorized:
                    return # nothing we can do
        
            # Check for an existing object.  If it is a content object, then we don't
            # try to replace it; there may be other attributes we shouldn't replace,
            # but because there are some always replaceable attributes, this is the
            # only type of filter we can reasonably expect to work.
            exists = False
            # Optimization for BTreeFolders
            if base_hasattr(contained_by, 'has_key'):
                exists = contained_by.has_key(id)
            # Otherwise check object ids (using getattr can trigger Unauth exceptions)
            elif base_hasattr(contained_by, 'objectIds'):
                exists = id in contained_by.objectIds()
            if exists:
                try:
                    existing_obj = getattr(contained_by, id, None)
                    if base_hasattr(existing_obj, 'portal_type'):
                        return _(u'There is already an item named ${name} in this folder.',
                             mapping={u'name' : id})
                except Unauthorized:
                    # If we cannot access the object it is safe to assume we cannot
                    # replace it
                    return _(u'There is already an item named ${name} in this folder.',
                             mapping={u'name' : id})
        
            if hasattr(contained_by, 'checkIdAvailable'):
                try:
                    if not contained_by.checkIdAvailable(id):
                        return _(u'${name} is reserved.', mapping={u'name' : id})
                except Unauthorized:
                    pass # ignore if we don't have permission
        
            # containers may implement this hook to further restrict ids
            if hasattr(contained_by, 'checkValidId'):
                try:
                    contained_by.checkValidId(id)
                except Unauthorized:
                    raise
                except ConflictError:
                    raise
                except:
                    return _(u'${name} is reserved.', mapping={u'name' : id})
        
            # make sure we don't collide with any parent method aliases
            portal_types = getToolByName(self, 'portal_types', None)
            if plone_utils is not None and portal_types is not None:
                parentFti = portal_types.getTypeInfo(contained_by)
                if parentFti is not None:
                    aliases = plone_utils.getMethodAliases(parentFti)
                    if aliases is not None:
                        for alias in aliases.keys():
                            if id == alias:
                                return _(u'${name} is reserved.', mapping={u'name' : id})
        
            # The last control on skin ids is not done ....


registerType(PhantasySkinImage, PROJECTNAME)

