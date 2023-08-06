# -*- coding: utf-8 -*-


"""
$Id: permissions.py,v 1.1 2006/07/26 09:05:21 jmgrimaldi Exp $
"""
__author__  = ''
__docformat__ = 'restructuredtext'

# CMF imports
from Products.CMFCore.permissions import setDefaultRoles

# Archetypes imports
from Products.Archetypes.public import listTypes

# Products imports
from collective.phantasy.config import PROJECTNAME

TYPE_ROLES = ('Manager')

permissions = {}
def wireAddPermissions():
    """Creates a list of add permissions for all types in this project
    
    Must be called **after** all types are registered!
    """
    
    global permissions
    all_types = listTypes(PROJECTNAME)
    for atype in all_types:
        permission = "%s: Add %s" % (PROJECTNAME, atype['portal_type'])
        setDefaultRoles(permission, TYPE_ROLES)
        permissions[atype['portal_type']] = permission
    return permissions
