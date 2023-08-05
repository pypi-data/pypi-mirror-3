
from Products.CMFCore.utils import ContentInit
from Products.CMFCore.FSFile import FSFile
from Products.CMFCore.DirectoryView import registerFileExtension
from Products.Archetypes.public import process_types, listTypes
from collective.phantasy.config import PROJECTNAME
from permissions import permissions, wireAddPermissions
import content
wireAddPermissions()   
import extendcontents
registerFileExtension('zip', FSFile)

def initializeContents(context):
    """Initialize phantasy types"""

    type_list = listTypes(PROJECTNAME)
    content_types, constructors, ftis = process_types(type_list, PROJECTNAME)

    # Assign an own permission to all content types
    all_types = zip(content_types, constructors)
    for atype, constructor in all_types:
        kind = "%s: %s" % (PROJECTNAME, atype.archetype_name)
        errors=[]
        ContentInit(
            kind,
            content_types      = (atype,),
            permission         = permissions[atype.portal_type],
            extra_constructors = (constructor,),
            fti                = ftis,
            ).initialize(context)  

            
