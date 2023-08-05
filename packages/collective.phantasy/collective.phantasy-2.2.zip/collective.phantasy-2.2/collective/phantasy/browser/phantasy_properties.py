# -*- coding: utf-8 -*-

import os
from App.Common import rfc1123_date
from DateTime import DateTime
from App.special_dtml import DTMLFile

# Zope imports
import zope.component
from zope.interface import implements
from Acquisition import aq_inner

# Plone, CMF, Five imports
from Products.ResourceRegistries.tools.packer import CSSPacker
from Products.Five import BrowserView
from interfaces import IPhantasyThemeProperties

this_dir = os.path.dirname(os.path.abspath(__file__))
templates_dir = os.path.join(this_dir, 'css')
stylesheet_dtml = DTMLFile('collective.phantasy.css', templates_dir)

class PhantasyThemeProperties(BrowserView):
    """ theme properties for phantasy.css """

    implements(IPhantasyThemeProperties)
    """
    this view is used by css template, and is rendered in the phantasyskin context.
    """
    stylesheet_dtml = stylesheet_dtml

    def __call__(self, *args, **kw):
        """Return a dtml file when calling the view (more easy thx to Gillux)"""

        # Wrap acquisition context to template
        context = aq_inner(self.context)
        template = self.stylesheet_dtml.__of__(context)
        # Push cache headers
        self.getHeader()
        phantasy_props = self.getPhantasyCssProperties()
        csscontent = template(context,
                              phantasy_properties = phantasy_props,
                              css_url = self.getPhantasyThemeUrl(),
                              portal_url = self.getPortalUrl() )

        return  CSSPacker('safe').pack(csscontent)

    def getPloneCssProperties(self) :
        """
        return css properties based on base_properties
        """

        context = aq_inner(self.context)
        dict_properties = {}
        bp = context.base_properties
        bpdict = bp.propdict()
        for k,v in bpdict.items() :
            if bp.hasProperty(k):
                dict_properties[k] = bp.getProperty(k)

        return dict_properties

    def getPhantasyCssProperties(self) :
        """
        return css dynamic properties
        """

        context = aq_inner(self.context)
        plone_properties = self.getPloneCssProperties()
        phantasy_properties = context.Schema()
        final_properties = {}
        for k in phantasy_properties.keys() :
            accessor = phantasy_properties[k].getAccessor(context)
            if not(accessor()) and plone_properties.has_key(k):
                final_properties[k] = plone_properties[k]
            else :
                final_properties[k] = accessor()
        return final_properties

    def getPhantasyThemeUrl(self) :
        """
        return skin url if skin is not temporary
        """

        context = aq_inner(self.context)
        if not context.isTemporary():
            return context.absolute_url()
        return self.getPortalUrl()

    def getPortalUrl(self) :
        """
        return portal url
        """

        context = aq_inner(self.context)
        portal_state = zope.component.getMultiAdapter((context, self.request), name=u'plone_portal_state')
        return portal_state.portal_url()


    def getHeader(self):
        context = aq_inner(self.context)
        request = self.request
        response = request.RESPONSE
        charset = context.getCharset()
        response.setHeader('Content-Type', 'text/css;;charset=%s' %charset)
        refresh_css = request.get('refresh_css', '')
        if not refresh_css :
            duration = 20
            seconds = float(duration)*24.0*3600.0
            response.setHeader('Expires',
                                rfc1123_date((DateTime() + duration).timeTime()))
            response.setHeader('Cache-Control',
                               'max-age=%d' % int(seconds))


