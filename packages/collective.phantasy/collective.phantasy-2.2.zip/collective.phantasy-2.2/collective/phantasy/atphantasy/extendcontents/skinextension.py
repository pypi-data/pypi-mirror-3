import zope.interface
import zope.component
from zope.app.component.hooks import getSite
from archetypes.schemaextender.interfaces import IOrderableSchemaExtender, IBrowserLayerAwareExtender
from archetypes.schemaextender.field import ExtensionField
from Products.Archetypes import atapi
from Products.CMFCore.utils import getToolByName

from collective.phantasy.widget import PhantasyBrowserWidget
from collective.phantasy.interfaces import IPhantasyBrowserLayer
from collective.phantasy import phantasyMessageFactory as _


class ISkinnable(zope.interface.Interface):
    """A Skinnable content item.
    """


class SkinField(ExtensionField, atapi.ReferenceField):
    """
      A schema extended field based on reference field
    """
    def getPhantasySkinType(self) :
        """Phantasy Skin Type depend on portal_properties"""
        portal = getSite()
        stp = getToolByName(portal, 'portal_properties').site_properties
        return (stp.getProperty('phantasy_skin_portal_type', 'PhantasySkin').strip('\n'),)

    allowed_types = property(fget = getPhantasySkinType)




class PhantasySkinSchemaExtender(object):
    zope.interface.implements(IOrderableSchemaExtender, IBrowserLayerAwareExtender)
    zope.component.adapts(ISkinnable)

    layer = IPhantasyBrowserLayer

    _fields = [
               SkinField('local_phantasy_skin',
                   schemata='default',
                   accessor = 'getLocal_phantasy_skin',
                   multiValued=0,
                   relationship='Rel1',
                   languageIndependent=True,
                   widget=PhantasyBrowserWidget(
                        force_close_on_insert= 1,
                        multiValued=0,
                        show_indexes=0,
                        allow_browse=1,
                        show_results_without_query=1,
                        image_portal_types = ('PhantasySkin'),
                        image_method = 'screenshot_thumb',
                        allow_search=0,
                        label = _("Phantasy Skin"),
                        description=_('help_select_skin', default=u"Browse for a skin."),
               )),
             ]


    def __init__(self, context):
        self.context = context

    def getFields(self):
        return self._fields

    def getOrder(self, original):
        defschemata = original['default']
        idx = defschemata.index('title')
        defschemata.remove('local_phantasy_skin')
        defschemata.insert(idx+1, 'local_phantasy_skin')
        return original
