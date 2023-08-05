# -*- coding: utf-8 -*-

"""
content-type used as Skin
TODO :
- import csv files to set skin data
"""

# Python imports
import os
import string
import unicodedata
import re
from zipfile import ZipFile
import tarfile

# Zope imports
from Acquisition import aq_base
from zope.interface import implements
from AccessControl import ClassSecurityInfo
from ComputedAttribute import ComputedAttribute

# CMF imports
from Products.CMFCore import permissions as CCP
from Products.CMFCore.exceptions import BadRequest
from Products.CMFPlone.utils import getToolByName

from plone.app.layout.navigation.interfaces import INavigationRoot
from Products.Archetypes.public import *

# Products imports
from Products.ATContentTypes.content.base import ATCTOrderedFolder
from Products.ATContentTypes.content.schemata import ATContentTypeSchema
from Products.ATContentTypes.content.schemata import NextPreviousAwareSchema
from Products.ATContentTypes.lib.constraintypes import ConstrainTypesMixinSchema


from collective.phantasy.atphantasy.interfaces import IPhantasySkin
from phantasyschema import PhantasyFieldsSchema, finalizePhantasySchema
from collective.phantasy.config import PROJECTNAME
from collective.phantasy import phantasyMessageFactory as _


IMAGE_UPLOAD_TYPE = "PhantasySkinImage"
FILE_UPLOAD_TYPE = "PhantasySkinFile"
IMAGES_EXTENSIONS = (".jpg",".gif",".jpeg",".png")

StandardFolderSchema =  ATContentTypeSchema.copy() + ConstrainTypesMixinSchema + NextPreviousAwareSchema

PhantasySkinSchema = StandardFolderSchema + PhantasyFieldsSchema.copy()

PhantasySkinSchema = finalizePhantasySchema(PhantasySkinSchema)


class PhantasySkin(ATCTOrderedFolder):
    """Phantasy Skin folder"""

    portal_type = meta_type = 'PhantasySkin'
    archetype_name = 'Phantasy Skin'
    global_allow = True
    filter_content_types = True
    allowed_content_types = ('PhantasySkinImage','PhantasySkinFile',)
    schema = PhantasySkinSchema
    implements(IPhantasySkin)


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
        # we do not want Language attributes for skin
        self.setLanguage('')
        # initialize standard plone properties in skin (all these properties are required)
        for fieldName in self.Schema().keys() :
            field = self.getField(fieldName)
            value = self.getDefaultValueForField(fieldName)
            if value :
                field.set(self, value, **kwargs)

    security.declarePrivate('getDefaultValueForField')
    def getDefaultValueForField (self, fieldName):
        """values for plone skin properties
           return a Plone css base property value if this property exists
        """
        ploneCssProperties = self.getPloneCssProperties()
        if ploneCssProperties.has_key(fieldName) :
            return ploneCssProperties[fieldName]

    security.declareProtected(CCP.View, 'getPloneCssProperties')
    def getPloneCssProperties(self) :
        """
        return static css properties based on actual plone theme
        """

        dict_properties = {}
        bp = self.base_properties
        bpdict = bp.propdict()
        for k,v in bpdict.items() :
            if bp.hasProperty(k):
                dict_properties[k] = bp.getProperty(k)

        return dict_properties

    security.declarePrivate('extractZipFile')
    def extractZipFile(self, zipFile):
        """
        Extract file in a zip
        """
        zip = ZipFile(zipFile,"r",8)
        file_list = {}
        type_list = {}
        for filename in zip.namelist():
            path,newfilename = os.path.split(filename)
            name, ext = os.path.splitext(filename)
            ext = string.lower(ext)
            data = zip.read(filename)
            if(len(data)):
                file_list[newfilename] = data
            if ext in IMAGES_EXTENSIONS :
                type_list[newfilename] = 'image'
            elif ext == '.ico':
                type_list[newfilename] = 'icon'
            elif ext=='.css' :
                type_list[newfilename] = 'cssfile'
            elif ext=='.js' :
                type_list[newfilename] = 'jsfile'
            else :
                type_list[newfilename] = 'file'
        return file_list, type_list

    security.declarePrivate('extractTarFile')
    def extractTarFile(self, tarFile, ext):
        """
        Extract file in a tar
        """
        file_list = {}
        type_list = {}
        if(ext == '.tar'):
            tar = tarfile.open(mode="r|",fileobj=tarFile)
        elif(ext == '.gz'):
            tar = tarfile.open(mode="r|gz",fileobj=tarFile)
        elif(ext == '.bz2'):
            tar = tarfile.open(mode="r|bz2",fileobj=tarFile)
        for filename in tar:
            path,newfilename = os.path.split(filename.name)
            name, ext = os.path.splitext(filename.name)
            ext = string.lower(ext)
            if filename.isfile() :
                data = tar.extractfile(filename)
                file_list[newfilename] = data.read()
                if ext in IMAGES_EXTENSIONS :
                    type_list[newfilename] = 'image'
                elif ext=='.css' :
                    type_list[newfilename] = 'cssfile'
                elif ext=='.js' :
                    type_list[newfilename] = 'jsfile'
                else :
                    type_list[newfilename] = 'file'
        return file_list, type_list

    security.declarePublic('createValidId')
    def createValidId(self, s):
        """
        Return a valid Zope id from the given string
        We do not use plone normalizer because
        we accept '_' in ids to overload skin images
        """

        try:
            id = s.decode('utf-8')
            id = unicodedata.normalize('NFKD', id)
            id = id.encode('ascii', 'ignore')
            sDecoded = True
        except:
            id=s
            sDecoded = False

        new_id = ''
        if sDecoded :
            for a in id:
                if a in string.digits or a in string.lowercase or a in string.uppercase or a=='.' or a==' ' or a=='-' or a=='_':
                    new_id += a
        else :
            for a in id:
                if a.lower() in 'abcdefghijklmnopqrstuvwxyz0123456789. -_':
                    new_id += a

        new_id = new_id.replace(' ','-')
        new_id = re.sub("-+","-", new_id)
        new_id = new_id.strip('_').lower()
        i=0
        incId = new_id
        while incId in self.objectIds():
            i+=1
            incId = str(i) + new_id

        return incId

    security.declareProtected(CCP.ModifyPortalContent, 'importImagesAndFiles')
    def importImagesAndFiles(self, zipFile, REQUEST=None):
        """
        Import images from a zipFile
        """
        putils = getToolByName(self, 'plone_utils')
        name, ext = os.path.splitext(zipFile.filename)
        ext = string.lower(ext)
        if(ext == '.zip'):
            filesAndTypesList = self.extractZipFile(zipFile)
            filesList = filesAndTypesList[0]
            typesList = filesAndTypesList[1]
        elif(ext in ['.tar','.gz','.bz2']):
            filesAndTypesList = self.extractTarFile(zipFile, ext)
            filesList = filesAndTypesList[0]
            typesList = filesAndTypesList[1]
        else:
            msg = "Error: wrong extention! File must be zip, tar, gz or bz2"
            putils.addPortalMessage(msg)
            if(REQUEST):
                REQUEST.RESPONSE.redirect("%s/phantasyskin_import" %self.absolute_url())

            return msg

        for key in filesList:
            data = str(filesList[key])
            idObj=self.createValidId(key)
            sprout=idObj.split('.')
            Title = '.'.join(sprout[:len(sprout)-1]).replace('_',' ')
            if typesList[key] in ('image', 'icon'):
                self.invokeFactory(IMAGE_UPLOAD_TYPE, idObj,
                                   title=Title, RESPONSE=None)
                skinImage = getattr(self, idObj)
                skinImage.setImage(str(data))
                imagefield = skinImage.getPrimaryField()
                imagefield.setFilename(skinImage, idObj)
                if typesList[key] == 'icon' :
                    skinImage.setContentType('image/x-icon')
            else :
                self.invokeFactory(FILE_UPLOAD_TYPE, idObj,
                                   title=Title, RESPONSE=None)
                skinFile = getattr(self, idObj)
                skinFile.setFile(str(data))
                filefield = skinFile.getPrimaryField()
                filefield.setFilename(skinFile, idObj)
                if typesList[key] == 'cssfile':
                    skinFile.setContentType('text/css')
                    if not self.getField('cssfile').getAccessor(self)():
                        self.getField('cssfile').getMutator(self)(idObj)

                # will be used in future
                elif typesList[key] == 'jsfile' :
                       skinFile.setContentType('text/javascipt')

        msg = _('label_imported_files',
                default=u"Imported ${num} images and files from file",
                mapping={'num': len(filesList)})
        putils.addPortalMessage(msg)
        if(REQUEST):
            REQUEST.RESPONSE.redirect("%s/view" %self.absolute_url())

        return msg

    # methods used for screenshots

    security.declareProtected(CCP.View, 'tag')
    def tag(self, **kwargs):
        """Generate image tag using the api of the ImageField
        """
        return self.getField('screenshot').tag(self, **kwargs)

    security.declareProtected(CCP.View, 'get_size')
    def get_size(self):
        """ZMI / Plone get size method

        BBB: ImageField.get_size() returns the size of the original image + all
        scales but we want only the size of the original image.
        """
        img = self.getScreenshot()
        if not getattr(aq_base(img), 'get_size', False):
            return 0

        return img.get_size()

    security.declareProtected(CCP.View, 'getSize')
    def getSize(self, scale=None):
        field = self.getField('screenshot')
        return field.getSize(self, scale=scale)

    security.declareProtected(CCP.View, 'getWidth')
    def getWidth(self, scale=None):
        return self.getSize(scale)[0]

    security.declareProtected(CCP.View, 'getHeight')
    def getHeight(self, scale=None):
        return self.getSize(scale)[1]

    width = ComputedAttribute(getWidth, 1)
    height = ComputedAttribute(getHeight, 1)

    security.declarePublic('get_phantasy_relative_path')
    def get_phantasy_relative_path(self) :
        """
        Return Phantasy Skin path
        relative to navigation root
        can be used to upload files
        """
        root = self
        portal_url = getToolByName(self, 'portal_url')
        portal = portal_url.getPortalObject()
        while not (INavigationRoot.providedBy(root) or root is portal) :
            root = root.aq_parent

        rootPath = root.getPhysicalPath()
        physical_path = self.getPhysicalPath()
        relative_path = physical_path[len(rootPath):]
        return '/'.join(relative_path)


    def _checkId(self, id, allow_dup=0):
        # allow overriding skinned names and tools for all users
        # for file name ids only
        if id[:2] == '@@':
            raise BadRequest('The id "%s" is invalid because it begins with '
                             '"@@".' % id)
        elif len(id.split('.')[-1]) == 3:
            return
        else:
            return super(PhantasySkin, self)._checkId(id, allow_dup=allow_dup)


    def __bobo_traverse__(self, REQUEST, name):
        """Transparent access to image scales
        """
        if name.startswith('screenshot'):
            field = self.getField('screenshot')
            image = None
            if name == 'screenshot':
                image = field.getScale(self)
            else:
                scalename = name[len('screenshot_'):]
                if scalename in field.getAvailableSizes(self):
                    image = field.getScale(self, scale=scalename)

            if image is not None and not isinstance(image, basestring):
                # image might be None or '' for empty images
                return image

        return ATCTOrderedFolder.__bobo_traverse__(self, REQUEST, name)


registerType(PhantasySkin, PROJECTNAME)
