# -*- coding: utf-8 -*-


# Zope imports
from zope.interface import implements
from Acquisition import aq_inner
from zope.component import getMultiAdapter

# Plone, Five imports
from Products.Five import BrowserView
# Product imports
from interfaces import IPhantasySkinView, IPhantasySkinImport


class PhantasySkinView(BrowserView):
    """ view for skin view template"""

    implements(IPhantasySkinView)

    def getSkinContents (self):
        """
        return images and files
        for phantasy album view
        """
        context = aq_inner(self.context)
        result = {}
        result['images'] = context.getFolderContents({'portal_type':('PhantasySkinImage',)},
                                                     full_objects=True)
        # css and other skin files
        result['files'] = context.getFolderContents({'portal_type':'PhantasySkinFile'})

        return result

    def getPortalUrl(self):
        portal_state = getMultiAdapter((self.context, self.request), name=u'plone_portal_state')
        return portal_state.portal_url()



class PhantasySkinImport(BrowserView):
    """ view for skin import template """

    implements(IPhantasySkinImport)

    def getPortalUrl(self):
        portal_state = getMultiAdapter((self.context, self.request), name=u'plone_portal_state')
        return portal_state.portal_url()



