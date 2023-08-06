import re
import urlparse
import random

from zope.component import getMultiAdapter
from Acquisition import aq_inner

from Products.CMFPlone.utils import getToolByName, base_hasattr
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from plone.app.layout.viewlets.common import (
     ViewletBase, SearchBoxViewlet, PathBarViewlet,
     GlobalSectionsViewlet, PersonalBarViewlet, SiteActionsViewlet,
     FooterViewlet as BaseFooterViewlet)
from plone.app.layout.viewlets.content import (
     DocumentActionsViewlet, DocumentBylineViewlet)
from plone.memoize.compress import xhtml_compress
from plone.memoize.instance import memoize

from collective.phantasy.atphantasy.interfaces import IPhantasySkin



def _getValueForField(skin, fieldname):
    """
    return a phantasySkin field value
    """
    schema = skin.Schema()
    accessor = schema[fieldname].getAccessor(skin)
    if accessor():
        return accessor()

class PhantasyHeaderViewlet(ViewletBase):

    render = ViewPageTemplateFile('templates/phantasy-header.pt')

    @memoize
    def get_cooked_css_url(self):
        """
         return cooked_css_list_urls
         = all parents skins url
        """
        context = aq_inner(self.context)
        portal_state = getMultiAdapter((context, self.request), name=u'plone_portal_state')
        portal = portal_state.portal()
        cooked_css = []
        parent = context
        while parent != portal:
            parent = aq_inner(parent.aq_parent)
            parent_skin = parent.restrictedTraverse('@@getPhantasySkin')
            if parent_skin():
                pskin = aq_inner(parent_skin())
                if base_hasattr(pskin, "getCssfile"):
                     if pskin.getCssfile():
                         cooked_css.append('%s/%s' %(pskin.absolute_url(),pskin.getCssfile()))

                cooked_css.append('%s/collective.phantasy.css' %pskin.absolute_url())

        cooked_css.reverse()
        return cooked_css

    def getPhantasyThemeUrl(self):
        """
         todo: improve with zope3 technologies (>>>>> Gilles au boulot)
        """
        context = aq_inner(self.context)
        skin = self.getPhantasySkinObject()
        if skin:
             return '%s/collective.phantasy.css' %skin.absolute_url()

        portal_state = getMultiAdapter((context, self.request), name=u'plone_portal_state')
        return portal_state.portal_url()

    def getPhantasySkinObject(self):
        """
          return skin object if exists
        """
        context = aq_inner(self.context)
        skin = context.restrictedTraverse('@@getPhantasySkin')
        if skin():
            return aq_inner(skin())

    def update(self):
        """
         refresh cooked_css_list_urls
         to improve
        """

        context = aq_inner(self.context)
        self.cooked_css_url = self.get_cooked_css_url()
        refresh_css=''
        skin = self.getPhantasySkinObject()
        if skin:
            if IPhantasySkin.providedBy(context) or 1:
                # on skin object we must only see the actuel skin
                self.cooked_css_url = []
                # no cache when we are on skin object
                refresh_css = '?refresh_css=%s' % random.randint(1, 20000000)

            self.cooked_css_url.append('%s/collective.phantasy.css%s' %(skin.absolute_url(),refresh_css))
            if skin.getCssfile():
                self.cooked_css_url.append('%s/%s%s' %(skin.absolute_url(),skin.getCssfile(),refresh_css))



class PhantasyViewletBase(ViewletBase):
    """ Base class for skin viewlets override
    """

    def absolutiseUrls(self, target, text):
        """ render links absolute in text
            used in phantasy viewlets
        """
        context = aq_inner(self.context)
        # '/' added at end because skin is a folderish
        # to be more generic just test if target is folderish
        # TODO ...
        obj_url = target.absolute_url() + '/'
        rc = getToolByName(context, 'reference_catalog')

        def _replace_locale_url(match):
            """Compute local url
            """
            url = str(match.group('url'))
            attribute =  str(match.group('attribute'))
            if match.group('protocol') is not None:
                url = '%s%s' % (match.group('protocol'), url)
            elif 'resolveuid/' in url.lower():
                rpaths = url.split('/')
                for i in range(0, len(rpaths)+1):
                    if rpaths[i].lower() == 'resolveuid':
                        break

                if len(rpaths) > i+1:
                    uid = rpaths[i+1]
                    obj = rc.lookupObject(uid)
                    if len(rpaths) > i+2:
                        subtraversal = '/' + '/'.join(rpaths[i+2:])
                    else:
                        subtraversal = ''

                    if not obj:
                        pass
                    else:
                        url = obj.absolute_url() + subtraversal

                else:
                    pass
            else:
                try:
                    url=urlparse.urljoin(obj_url, url)
                except:
                    pass

            return '%s="%s"' % (attribute,url)
            return match.group(0)

        abs_url = re.compile('(?P<attribute>href|src)\s*=\s*([\'\"])(?P<protocol>(ht|f)tps?)?(?P<url>[^\"\']*)\\2', re.IGNORECASE)
        text = abs_url.sub(_replace_locale_url, text)

        return text

    @memoize
    def getFirstPhantasySkinObject(self):
        """return skin associated with parents
        """
        context = aq_inner(self.context)
        portal_state = getMultiAdapter((context, self.request), name=u'plone_portal_state')
        portal = portal_state.portal()
        parent = context
        skin = getMultiAdapter((parent, self.request), name=u'getPhantasySkin')
        if skin() is not None:
            return aq_inner(skin())

        while parent != portal:
            parent = aq_inner(parent.aq_parent)
            skin = getMultiAdapter((parent, self.request), name=u'getPhantasySkin')
            if skin() is not None:
                return aq_inner(skin())


class PhantasyFaviconViewlet(PhantasyViewletBase):

    _template = ViewPageTemplateFile('templates/phantasy-favicon.pt')

    def favicon_url(self):
        skin = self.getFirstPhantasySkinObject()
        if skin and 'favicon.ico' in skin:
            return '%s/image' % skin['favicon.ico'].absolute_url()
        else:
            return '%s/favicon.ico' % self.site_url

    def render(self):
        return xhtml_compress(self._template())


class FooterViewlet(PhantasyViewletBase, BaseFooterViewlet):
    """ Base class for skin footer override
    """

    index = ViewPageTemplateFile('templates/phantasy-footer.pt')
    def getSkinFooter(self):
        """
          return current phantasy skin footer
        """
        skin = self.getFirstPhantasySkinObject()
        if skin is not None:
            return self.absolutiseUrls(skin, skin.getFooterViewlet())

    def update(self):
        super(FooterViewlet, self).update()
        self.skin_footer = self.getSkinFooter()


class ColophonViewlet(PhantasyViewletBase):
    """ Base class for skin colophon override
    """

    index = ViewPageTemplateFile('templates/phantasy-colophon.pt')
    def getSkinColophon(self):
        """
          return current phantasy skin colophon
        """

        skin = self.getFirstPhantasySkinObject()
        if skin is not None:
            return self.absolutiseUrls(skin, skin.getColophonViewlet())

    def update(self):
        self.skin_colophon = self.getSkinColophon()


class LogoViewlet(PhantasyViewletBase):
    """ Base class for logo viewlet override
    """

    index = ViewPageTemplateFile('templates/phantasy-logo.pt')
    def getSkinLogo(self):
        """
          return current phantasy skin logo viewlet
        """

        skin = self.getFirstPhantasySkinObject()
        if skin is not None:
            return self.absolutiseUrls(skin, skin.getLogoViewlet())

    def update(self):
        context = aq_inner(self.context)
        portal_state = getMultiAdapter((context, self.request), name=u'plone_portal_state')
        portal = portal_state.portal()
        logoName = portal.restrictedTraverse('base_properties').logoName
        self.logo_tag = portal.restrictedTraverse(logoName).tag()
        self.navigation_root_url = portal_state.navigation_root_url()
        self.skin_logo = self.getSkinLogo()


class DisplayViewletBase(PhantasyViewletBase):
    """
    base class for display or not the viewlet
    """

    def emptyindex(self):
        return u''

    fieldname  = ''

    @memoize
    def displayViewlet(self):
        fieldname = self.fieldname
        skin = self.getFirstPhantasySkinObject()
        if skin is not None and fieldname:
            if not _getValueForField(skin, fieldname):
                return False
        return True


class PhantasySearchBoxViewlet(SearchBoxViewlet, DisplayViewletBase):
    """ Base class for searchbox viewlet override
        return an empy index if display is False in skin object
    """

    fieldname = 'displaySearchBoxViewlet'

    def update(self):
        if self.displayViewlet():
            SearchBoxViewlet.update(self)
        else:
            self.index = self.emptyindex


class PhantasyPathBarViewlet(PathBarViewlet, DisplayViewletBase):
    """ Base class for breadcrumbs viewlet override
        return an empy index if display is False in skin object
    """

    fieldname = 'displayBreadCrumbsViewlet'

    def update(self):
        if self.displayViewlet():
            PathBarViewlet.update(self)
        else:
            self.index = self.emptyindex


class PhantasyGlobalSectionsViewlet(GlobalSectionsViewlet, DisplayViewletBase):
    """ Base class for Global sections viewlet override
        return an empy index if display is False in skin object
    """

    fieldname = 'displayGlobalSectionsViewlet'

    def update(self):
        if self.displayViewlet():
            GlobalSectionsViewlet.update(self)
        else:
            self.index = self.emptyindex


class PhantasyPersonalBarViewlet(PersonalBarViewlet, DisplayViewletBase):
    """ Base class for Personal Bar viewlet override
        return an empy index if display is False in skin object
    """

    fieldname = 'displayPersonalBarViewlet'

    def update(self):
        if self.displayViewlet():
            PersonalBarViewlet.update(self)
        else:
            self.index = self.emptyindex


class PhantasySiteActionsViewlet(SiteActionsViewlet, DisplayViewletBase):
    """ Base class for Site actions viewlet override
        return an empy index if display is False in skin object
    """

    fieldname = 'displaySiteActionsViewlet'

    def update(self):
        if self.displayViewlet():
            SiteActionsViewlet.update(self)
        else:
            self.index = self.emptyindex


class PhantasyDocumentActionsViewlet(DocumentActionsViewlet, DisplayViewletBase):
    """ Base class for Document actions viewlet override
        return an empy index if display is False in skin object
    """

    fieldname = 'displayDocumentActionsViewlet'

    def update(self):
        if self.displayViewlet():
            DocumentActionsViewlet.update(self)
        else:
            self.index = self.emptyindex


class PhantasyDocumentBylineViewlet(DocumentBylineViewlet, DisplayViewletBase):
    """ Base class for Document By line Viewlet override
        return an empy index if display is False in skin object
    """

    fieldname = 'displayDocumentBylineViewlet'

    def update(self):
        if self.displayViewlet():
            DocumentBylineViewlet.update(self)
        else:
            self.index = self.emptyindex
