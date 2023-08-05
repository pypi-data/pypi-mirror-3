# -*- coding: utf-8 -*-

"""
PhantasySkinFile used for css, and perhaps other files 
used in skin (swf, js ...)
TODO: 
- do not use ATFile 
- use a textarea widget when contentType= 'text/*' to edit easily the content
- rename id according to file name (do the same thing for PhantasySkinImage)
"""


from zope.interface import implements
from DateTime import DateTime
from AccessControl import ClassSecurityInfo
from App.Common import rfc1123_date

from Products.CMFCore import permissions
from Products.Archetypes.public import *

# Products imports

from Products.ATContentTypes.content.file import ATFile
from Products.ATContentTypes.content.file import ATFileSchema
from collective.phantasy.atphantasy.interfaces import IPhantasySkinFile
from collective.phantasy.config import PROJECTNAME

PhantasySkinFileSchema = ATFileSchema.copy()
PhantasySkinFileSchema['description'].widget.visible = {'view':'invisible',
                                                         'edit':'invisible'}

class PhantasySkinFile(ATFile):
    """Phantasy Skin File for Collective Phantasy"""

    schema = PhantasySkinFileSchema
    security = ClassSecurityInfo()
    implements(IPhantasySkinFile)
    portal_type = meta_type = 'PhantasySkinFile'
    archetype_name = 'Phantasy Skin File'
    global_allow = False

    security.declarePrivate('initializeArchetype')
    def initializeArchetype(self, **kwargs):
        ATFile.initializeArchetype(self, **kwargs)
        # we do not want Language attributes for skinFile
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
        
        return ATFile.index_html(self, REQUEST, RESPONSE)                 

registerType(PhantasySkinFile, PROJECTNAME)

