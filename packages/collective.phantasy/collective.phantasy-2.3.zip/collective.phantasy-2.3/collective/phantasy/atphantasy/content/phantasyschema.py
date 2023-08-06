from Products.Archetypes.public import *
from collective.phantasy.config import I18N_DOMAIN
from Products.SmartColorWidget.Widget import SmartColorWidget
from Products.ATContentTypes.configuration import zconf
from Products.Archetypes.atapi import AnnotationStorage

from Products.validation.config import validation
from Products.validation.validators.SupplValidators import MaxSizeValidator
from Products.validation import V_REQUIRED

validation.register(MaxSizeValidator('checkImageMaxSize',
                                     maxsize=zconf.ATImage.max_file_size))

from collective.phantasy import phantasyMessageFactory as _

try:
    from iw.fss.FileSystemStorage import FileSystemStorage
    HAS_FSS = True
except :
    HAS_FSS = False

try:
    from Products.FCKeditor.FckWidget import FckWidget
    HAS_FCKWIDGET = True
except:
    HAS_FCKWIDGET = False

PRESERVED_SCHEMATAS = ['default', 'images', 'dimensions', 'colors', 'fonts', 'borders', 'plone-overloads', 'viewlets', 'dynamic-viewlets']

CUSTOM_TOOL_BAR  = """[
['Source','Preview','-','Templates'],
['Cut','Copy','Paste','PasteText','RemoveFormat'],
['Bold','Italic','Underline','StrikeThrough','-','Subscript','Superscript'],
['OrderedList','UnorderedList','-','Outdent','Indent'],
['Link','Unlink','Anchor','Image','imgmapPopup','Flash'],
['Style','FontFormat'],
['FitWindow']
]"""


def finalizePhantasySchema(schema):
    """Finalizes schema to alter some fields
    """
    # Id must be valid and make description invisible
    schema['id'].validators = ('isValidId',)
    schema['description'].widget.visible = {'view':'invisible', 'edit':'invisible'}
    # FSS Storage for skin screenshot if iw.fss is available
    if HAS_FSS :
        schema['screenshot'].storage = FileSystemStorage()
    for fieldName in schema.keys() :
        if schema[fieldName].schemata not in PRESERVED_SCHEMATAS :
            # hide ATCTFolder metadata fields unuseful for skins
            schema[fieldName].widget.visible = {'view':'invisible', 'edit':'invisible'}
        # FCKWidget for viewlet fields if FCK is available
        if HAS_FCKWIDGET and schema[fieldName].schemata == 'viewlets' :
            schema[fieldName].widget = FckWidget (
                            description = schema[fieldName].widget.description,
                            label = schema[fieldName].widget.label,
                            rows=12,
                            width = '100%',
                            height ='150px',
                            fck_toolbar = 'Custom',
                            fck_custom_toolbar = CUSTOM_TOOL_BAR,
                            file_portal_type = 'PhantasySkinFile',
                            image_portal_type = 'PhantasySkinImage',
                            browse_images_portal_types = ['PhantasySkinImage', 'Image'],
                            fck_force_other_path_method = 'get_phantasy_relative_path',
                            fck_force_other_root_method = 'get_phantasy_relative_path',
                            # force no paragraphs in viewlets
                            keyboard_entermode = 'div',
                            allow_link_byuid = False,
                            start_expanded = True,
                            allow_file_upload = False)
            if fieldName == 'logoViewlet' :
                css_id = 'portal-logo'
            elif fieldName == 'footerViewlet' :
                css_id = 'portal-footer'
            elif fieldName == 'colophonViewlet' :
                css_id = 'portal-colophon'
            schema[fieldName].widget.fck_area_css_id = css_id
            schema[fieldName].widget.fck_area_css_class = ''
    # Make a copy to reinitialize all layers
    new_schema = schema.copy()
    return new_schema



# in skin schema fields with same name as standard plone base_properties must always be required
PhantasyFieldsSchema = Schema((

    StringField(
        'cssfile',
        schemata ='default',
        widget=StringWidget(
                        description = _(u'description_css_file', u"""Enter a stylesheet file name, don't forget to upload the file in this skin.
This css will be applied at the end (after all properties). Use './myimage.jpg' in this css
to reference an image called 'myimage.jpg' from this skin."""),
                        label = _(u'label_css_file', u'Css File Name'),
            ),
        ),

    ImageField(
        'screenshot',
        required=False,
        primary=False,
        languageIndependent=True,
        storage = AnnotationStorage(migrate=True),
        swallowResizeExceptions = zconf.swallowImageResizeExceptions.enable,
        pil_quality = zconf.pil_config.quality,
        pil_resize_algo = zconf.pil_config.resize_algo,
        max_size = zconf.ATImage.max_image_dimension,
        sizes= {'large'   : (768, 768),
               'preview' : (400, 400),
               'mini'    : (200, 200),
               'thumb'   : (128, 128),
               'tile'    :  (64, 64),
               'icon'    :  (32, 32),
               'listing' :  (16, 16),
              },
        validators = (('checkImageMaxSize', V_REQUIRED)),
        widget = ImageWidget(
                description = _(u'description_phantasy_screenshot',
                                default=u'Upload a screen Shot for this skin, used to help users to select a skin'),
                label= _(u'label_phantasy_screenshot', default=u'Screen Shot'),
                show_content_type = False,
                preview_scale = 'mini',
                ),
        ),


# fields for viewlets overrides
    TextField('logoViewlet',
              schemata ='viewlets',
              required=False,
              searchable=False,
              validators = ('isTidyHtmlWithCleanup',),
              allowable_content_types = ('text/html',),
              default_content_type = 'text/html',
              default_output_type = 'text/x-html-safe',
              widget = RichWidget(
                        description = _(u'description_logo_viewlet', u"""Override the logo viewlet,
you can add images or links with rich editor"""),
                        label = _(u'label_logo_viewlet', u'Logo Viewlet'),
                        rows = 25,
                        allow_file_upload = False),
    ),

    TextField('footerViewlet',
              schemata ='viewlets',
              required=False,
              searchable=False,
              validators = ('isTidyHtmlWithCleanup',),
              allowable_content_types = ('text/html',),
              default_content_type = 'text/html',
              default_output_type = 'text/x-html-safe',
              widget = RichWidget(
                        description = _(u'description_footer_viewlet', u"""Override the footer viewlet,
you can add images or links with rich editor"""),
                        label = _(u'label_footer_viewlet', u'Footer Viewlet'),
                        rows = 25,
                        allow_file_upload = False),
    ),

    TextField('colophonViewlet',
              schemata ='viewlets',
              required=False,
              searchable=False,
              validators = ('isTidyHtmlWithCleanup',),
              allowable_content_types = ('text/html',),
              default_content_type = 'text/html',
              default_output_type = 'text/x-html-safe',
              widget = RichWidget(
                        description = _(u'description_colophon_viewlet', u"""Override the colophon viewlet,
you can add images or links with rich editor"""),
                        label = _(u'label_colophon_viewlet', u'Colophon Viewlet'),
                        i18n_domain = I18N_DOMAIN,
                        rows = 25,
                        allow_file_upload = False),
    ),

    BooleanField(
        'displaySearchBoxViewlet',
        schemata ='dynamic-viewlets',
        default = True,
        widget=BooleanWidget(
            description = _(u'description_display_searchbox_viewlet',
                                u"""Do you want to display the searchbox viewlet with live search in header ?"""),
            label = _(u'label_display_searchbox_viewlet', u'Display Searchbox ?'),
            ),
        ),

    BooleanField(
        'displayBreadCrumbsViewlet',
        schemata ='dynamic-viewlets',
        default = True,
        widget=BooleanWidget(
            description = _(u'description_display_breadcrumbs_viewlet',
                                u"""Do you want to display the breadcrumbs viewlet in top of content ?"""),
            label = _(u'label_display_breadcrumbs_viewlet', u'Display Bread Crumbs ?'),
            ),
        ),

    BooleanField(
        'displayGlobalSectionsViewlet',
        schemata ='dynamic-viewlets',
        default = True,
        widget=BooleanWidget(
            description = _(u'description_display_globalsections_viewlet',
                                u"""Do you want to display the global sections viewlet (horizontal navigation at top) ?"""),
            label = _(u'label_display_globalsections_viewlet', u'Display Global Sections ?'),
            ),
        ),

    BooleanField(
        'displayPersonalBarViewlet',
        schemata ='dynamic-viewlets',
        default = True,
        widget=BooleanWidget(
            description = _(u'description_display_personalbar_viewlet',
                                u"""Do you want to display the personal bar viewlet (links : login, preferences ...) ?"""),
            label = _(u'label_display_personalbar_viewlet', u'Display Personal Bar ?'),
            ),
        ),

    BooleanField(
        'displaySiteActionsViewlet',
        schemata ='dynamic-viewlets',
        default = True,
        widget=BooleanWidget(
            description = _(u'description_display_siteactions_viewlet',
                                u"""Do you want to display the site actions viewlet (links : site map, contact ...) ?"""),
            label = _(u'label_display_siteactions_viewlet', u'Display Site Actions ?'),
            ),
        ),

    BooleanField(
        'displayDocumentActionsViewlet',
        schemata ='dynamic-viewlets',
        default = True,
        widget=BooleanWidget(
            description = _(u'description_display_documentactions_viewlet',
                                u"""Do you want to display the document actions viewlet (link: print, send this page ...) ?"""),
            label = _(u'label_display_documentactions_viewlet', u'Display Document Actions ?'),
            ),
        ),

    BooleanField(
        'displayDocumentBylineViewlet',
        schemata ='dynamic-viewlets',
        default = True,
        widget=BooleanWidget(
            description = _(u'description_display_documentbyline_viewlet',
                                u"""Do you want to display the document by line viewlet for each content (author, date and keywords) ?"""),
            label = _(u'label_display_documentbyline_viewlet', u'Display Document By Line ?'),
            ),
        ),

# fields for images
# logoName property is no more used in standard plone css
# so we make it invisible
    StringField(
        'logoName',
        schemata ='images',
        required=1,
        widget=StringWidget(
            label='Logo Name',
            visible = {'view':'invisible', 'edit':'invisible'},
            description = "Choose the logo file name, upload the image in the skin to overload it",
            i18n_domain = I18N_DOMAIN,
            ),
        ),
    StringField(
        'backgroundImageName',
        schemata ='images',
        widget=StringWidget(
            description = _(u'description_background_image_name', u"""Enter the background image name for the page, upload the image in this skin"""),
            label = _(u'label_background_image_name', u'Background Image Name'),
            ),
        ),
    StringField(
        'backgroundImagePosition',
        schemata ='images',
        default="top left",
        vocabulary = [("top left", _(u"Top Left")),
                      ("top right", _(u"Top Right")),
                      ("top center", _(u"Top Center")),
                      ("center left", _(u"Center Left")),
                      ("center right", _(u"Center Right")),
                      ("center center", _(u"Center Center")),
                      ("bottom left", _(u"Bottom Left")),
                      ("bottom right", _(u"Bottom Right")),
                      ("bottom center", _(u"Bottom Center"))],
        widget=SelectionWidget(
            description = _(u'description_background_image_position', u"""Choose the background image position for the page"""),
            label = _(u'label_background_image_position', u'Background Image Position'),
            format='select',
            ),
        ),
    StringField(
        'backgroundImageRepeat',
        schemata ='images',
        default="no-repeat",
        vocabulary = [("no-repeat", "No repeat"),
                      ("repeat-x", "Horizontal Repeat"),
                      ("repeat-y", "Vertical Repeat"),
                      ("repeat", "mosaic repeat")],
        widget=SelectionWidget(
            description = _(u'description_background_image_repeat', u"""Choose the background image repeat for the page"""),
            label = _(u'label_background_image_repeat', u'Background Image Repeat'),
            format='select',
            ),
        ),
    StringField(
        'portalBackgroundImageName',
        schemata ='images',
        widget=StringWidget(
            description = _(u'description_portal_background_image_name', u"""Enter the background image name for the portal, upload the image in this skin"""),
            label = _(u'label_portal_background_image_name', u'Portal Background Image Name'),
            ),
        ),
    StringField(
        'contentBackgroundImageName',
        schemata ='images',
        widget=StringWidget(
            description = _(u'description_content_background_image_name', u"""Choose the background image name for the content, upload the image in this skin"""),
            label = _(u'label_contentl_background_image_name', u'Content Background Image Name'),
            ),
        ),
    StringField(
        'headerBackgroundImageName',
        schemata ='images',
        widget=StringWidget(
            description = _(u'description_header_background_image_name', u"""Choose the background image name for the header, upload the image in this skin"""),
            label = _(u'label_header_background_image_name', u'Header Background Image Name'),
            ),
        ),
# this property is never used is standard plone css
# so we make it invisible
    StringField(
        'portalMinWidth',
        schemata ='dimensions',
        widget=StringWidget(
            label='Portal min width',
            visible = {'view':'invisible', 'edit':'invisible'},
            description = "Choose the portal min width in px em or %",
            ),
        ),
    StringField(
        'portalWidth',
        schemata ='dimensions',
        default = '100%',
        widget=StringWidget(
            description = _(u'description_portal_width', u"""Choose the portal min width in px em or %"""),
            label = _(u'label_portal_width', u'Portal width'),
            ),
        ),
    StringField(
        'portalHorizontalPosition',
        schemata ='dimensions',
        default="",
        vocabulary = [("0", _(u"undefined")),
                      ("0 auto 0 auto", _(u"centered")),
                      ("0 auto 0 0", _(u"on left")),
                      ("0 0 0 auto", _(u"on right"))],
        widget=SelectionWidget(
            description = _(u'description_portal_horizontal_position', u"""Choose the position for portal"""),
            label = _(u'label_portal_horizontal_position', u'Portal Horizontal Position'),
            format='select',
            ),
        ),
    StringField(
        'columnOneWidth',
        schemata ='dimensions',
        required=1,
        widget=StringWidget(
            description = _(u'description_column_one_width', u"""Choose the column one width in px em or %"""),
            label = _(u'label_column_one_width', u'Column One width'),
            ),
        ),
    StringField(
        'columnTwoWidth',
        schemata ='dimensions',
        required=1,
        widget=StringWidget(
            description = _(u'description_column_two_width', u"""Choose the column two width in px em or %"""),
            label = _(u'label_column_two_width', u'Column Two width'),
            ),
        ),
    StringField(
        'fontFamily',
        schemata ='fonts',
        required=1,
        widget=StringWidget(
            description = _(u'description_font_family',
                            u"""Choose the font family"""),
            label = _(u'label_font_family', u'Font Family'),
            ),
        ),
    StringField(
        'fontMainSize',
        schemata ='fonts',
        required=0,
        widget=StringWidget(
            description = _(u'description_font_main_size',
                            u"Choose the main font size in % (better) em px pt "
                            u"or using a keyword (xx-small, small, ...)"),
            label = _(u'label_font_main_size', u'Font Main Size'),
            ),
        ),
    StringField(
        'fontSmallSize',
        schemata ='fonts',
        required=1,
        widget=StringWidget(
            description = _(u'description_font_small_size',
                            u"Choose the small font size in % (better) em px pt "
                            u"or using a keyword (xx-small, small, ...)"""),
            label = _(u'label_font_small_size', u'Font Small Size'),
            ),
        ),
    StringField(
        'headingFontFamily',
        schemata ='fonts',
        required=1,
        widget=StringWidget(
            description = _(u'description_heading_font_family',
                            u"""Choose the font family for titles"""),
            label = _(u'label_heading_font_family', u'Heading Font Family'),
            ),
        ),
    StringField(
        'textTransform',
        schemata ='fonts',
        required=1,
        vocabulary = [("none", _(u"none")),
                      ("uppercase", _(u"uppercase")),
                      ("lowercase", _(u"lowercase")),
                      ("capitalize", _(u"capitalize"))],
        widget=SelectionWidget(
            description = _(u'description_text_transform',
                            u"""Choose the text transformation for tabs and some headings"""),
            label = _(u'label_text_transform', u'Text Transform'),
            format='select',
            ),
        ),
    StringField(
        'fontColor',
        schemata ='colors',
        required=1,
        widget=SmartColorWidget(
            description = _(u'description_font_color',
                            u"""Choose the font color"""),
            label = _(u'label_font_color', u'Font Color'),
            ),
        ),
    StringField(
        'backgroundColor',
        schemata ='colors',
        required=1,
        widget=SmartColorWidget(
            description = _(u'description_background_color',
                            u"""Choose the background color of the page"""),
            label = _(u'label_background_color', u'Background Color'),
            ),
        ),
    StringField(
        'discreetColor',
        schemata ='colors',
        required=1,
        widget=SmartColorWidget(
            description = _(u'description_discreet_color',
                            u"""Choose the discreet color (can be used in content) """),
            label = _(u'label_discreet_color', u'Discreet Color'),
            ),
        ),
    StringField(
        'portalBackgroundColor',
        schemata ='colors',
        default="transparent",
        widget=SmartColorWidget(
            description = _(u'description_portal_background_color',
                                u"""Choose the portal background color"""),
            label = _(u'label_portal_background_color', u'Portal Background Color'),
            ),
        ),
    StringField(
        'contentBackgroundColor',
        schemata ='colors',
        default="transparent",
        widget=SmartColorWidget(
            description = _(u'description_content_background_color',
                                u"""Choose background color for content part of the page"""),
            label = _(u'label_content_background_color', u'Content Background Color'),
            ),
        ),
    StringField(
        'personaltoolsBackgroundColor',
        schemata ='colors',
        default="#E3E3E3",
        widget=SmartColorWidget(
            description = _(u'description_personaltools_background_color',
                            u"""Choose background color for personal tools - language choice and user menu"""),
            label = _(u'label_personaltools_background_color',
                      u"Personal tools Background Color"),
            ),
        ),
    StringField(
        'personaltoolsFontColor',
        schemata ='colors',
        default="#205C90",
        widget=SmartColorWidget(
            description = _(u'description_personaltools_font_color',
                            u"""Choose font color for personal tools - language choice and user menu"""),
            label = _(u'label_personaltools_font_color',
                      u"Personal tools Font Color"),
            ),
        ),
    StringField(
        'headerBackgroundColor',
        schemata ='colors',
        default="transparent",
        widget=SmartColorWidget(
            description = _(u'description_header_background_color',
                                u"""Choose background color for the header"""),
            label = _(u'label_header_background_color', u"Header Background Color"),
            ),
        ),
    StringField(
        'globalNavBackgroundColor',
        schemata ='colors',
        default="#dee7ec",
        widget=SmartColorWidget(
            description = _(u'description_global_nav_background_color',
                            u"""Choose the background color of global navigation"""),
            label = _(u'label_global_nav_background_color', u'Global navigation Background Color'),
            ),
        ),
    StringField(
        'globalNavLinkColor',
        schemata ='colors',
        default="#205c90",
        widget=SmartColorWidget(
            description = _(u'description_global_nav_font_color',
                            u"""Choose the color of font and selected element background in global navigation"""),
            label = _(u'label_global_nav_font_color', u'Global navigation Font Color'),
            ),
        ),
    StringField(
        'inputFontColor',
        schemata ='colors',
        required=1,
        widget=SmartColorWidget(
            description = _(u'description_input_font_color',
                                u"""Choose the input fields font color"""),
            label = _(u'label_input_font_color', u'Input Font Color'),
            ),
        ),
    StringField(
        'linkColor',
        schemata ='colors',
        required=1,
        widget=SmartColorWidget(
            description = _(u'description_link_color',
                                u"""Choose the color for links"""),
            label = _(u'label_link_color', u'Link Color'),
            ),
        ),
    StringField(
        'linkVisitedColor',
        schemata ='colors',
        required=1,
        widget=SmartColorWidget(
            description = _(u'description_link_visited_color',
                                u"""Choose the color for visited links"""),
            label = _(u'label_link_visited_color', u'Link Visited Color'),
            ),
        ),
    StringField(
        'linkActiveColor',
        schemata ='colors',
        required=1,
        widget=SmartColorWidget(
            description = _(u'description_link_active_color',
                                u"""Choose the color for active links"""),
            label = _(u'label_link_active_color', u'Link Active/Hover Color'),
            ),
        ),
    StringField(
        'notifyBackgroundColor',
        schemata ='colors',
        required=1,
        widget=SmartColorWidget(
            description = _(u'description_notify_background_color',
                                u"""Choose the notify background color (for portal messages)"""),
            label = _(u'label_notify_background_color', u'Notify Background Color'),
            ),
        ),
    StringField(
        'notifyBorderColor',
        schemata ='colors',
        required=1,
        widget=SmartColorWidget(
            description = _(u'description_notify_border_color',
                                u"""Choose the notify border color"""),
            label = _(u'label_notify_border_color', u'Notify Border Color'),
            ),
        ),
    StringField(
        'helpBackgroundColor',
        schemata ='colors',
        required=1,
        widget=SmartColorWidget(
            description = _(u'description_help_background_color',
                                u"""Choose the bg color for help in forms"""),
            label = _(u'label_help_background_color', u'Help Background Color'),
            ),
        ),
    StringField(
        'oddRowBackgroundColor',
        schemata ='colors',
        required=1,
        default="#EEEEEE",
        widget=SmartColorWidget(
            description = _(u'description_odd_row_background_color',
                                u"""Choose the bg color for odd rows (tables, portlets)"""),
            label = _(u'label__odd_row_background_color', u'Odd Row Background Color'),
            ),
        ),
    StringField(
        'evenRowBackgroundColor',
        schemata ='colors',
        required=1,
        widget=SmartColorWidget(
            description = _(u'description_even_row_background_color',
                                u"""Choose the bg color for even rows (tables, portlets)"""),
            label = _(u'label__even_row_background_color', u'Even Row Background Color'),
            ),
        ),
    StringField(
        'globalBackgroundColor',
        schemata ='colors',
        required=1,
        widget=SmartColorWidget(
            description = _(u'description_global_background_color',
                                u"""Choose the global background color (used in tabs and portlets headers)"""),
            label = _(u'label_global_background_color', u'Global Background Color'),
            ),
        ),
    StringField(
        'globalFontColor',
        schemata ='colors',
        required=1,
        widget=SmartColorWidget(
            description = _(u'description_global_font_color',
                                u"""Choose the global font color"""),
            label = _(u'label_global_font_color', u'Global Font Color'),
            ),
        ),
    StringField(
        'globalBorderColor',
        schemata ='colors',
        required=1,
        widget=SmartColorWidget(
            description = _(u'description_global_border_color',
                                u"""Choose the color for global borders"""),
            label = _(u'label_global_border_color', u'Global Border Color'),
            ),
        ),
    StringField(
        'contentViewBackgroundColor',
        schemata ='colors',
        required=1,
        widget=SmartColorWidget(
            description = _(u'description_content_views_background_color',
                                u"""Choose the background color for content views tabs"""),
            label = _(u'label_content_views_background_color', u'Content View Background Color'),
            ),
        ),
    StringField(
        'contentViewBorderColor',
        schemata ='colors',
        required=1,
        widget=SmartColorWidget(
            description = _(u'description_content_views_border_color',
                                u"""Choose the border color for content views tabs"""),
            label = _(u'label_content_views_border_color', u'Content View Border Color'),
            ),
        ),
    StringField(
        'contentViewFontColor',
        schemata ='colors',
        required=1,
        widget=SmartColorWidget(
            description = _(u'description_content_views_font_color',
                                u"""Choose the font color for content views tabs"""),
            label = _(u'label_content_views_font_color', u'Content View Font Color'),
            ),
        ),
    StringField(
        'listingHeadersFontColor',
        schemata ='colors',
        required=1,
        default="#666666",
        widget=SmartColorWidget(
            description = _(u'description_listing_headers_font_color',
                                u"""Choose the font color for the text of listing headers"""),
            label = _(u'label_listing_headers_font_color', u'Listing Headers Font Color'),
            ),
        ),
    StringField(
        'portletHeadersFontColor',
        schemata ='colors',
        required=1,
        default="#000000",
        widget=SmartColorWidget(
            description = _(u'description_portlet_headers_font_color',
                                u"""Choose the font color for the text of portlet headers"""),
            label = _(u'label_portlet_headers_font_color', u'Portlet Headers Font Color'),
            ),
        ),
    StringField(
        'borderStyle',
        schemata ='borders',
        required=1,
        vocabulary = [("none", "no border"),
                      ("hidden", "hidden when none is impossible (tables)"),
                      ("solid", "solid"),
                      ("dotted", "dotted"),
                      ("dashed", "dashed"),
                      ("groove","3D groove"),
                      ("double", "double borders"),
                      ("inset", "3D inset"),
                      ("outset","3D outset"),
                      ("ridge","3D ridge")],
        widget=SelectionWidget(
            description = _(u'description_border_style',
                                u"""Choose the global border style"""),
            label = _(u'label_border_style', u'Border Style'),
            format='select',
            ),
        ),
    StringField(
        'borderStyleAnnotations',
        schemata ='borders',
        required=1,
        vocabulary = [("none", "no border"),
                      ("hidden", "hidden when none is impossible (tables)"),
                      ("solid", "solid"),
                      ("dotted", "dotted"),
                      ("dashed", "dashed"),
                      ("groove","3D groove"),
                      ("double", "double borders"),
                      ("inset", "3D inset"),
                      ("outset","3D outset"),
                      ("ridge","3D ridge")],
        widget=SelectionWidget(
            description = _(u'description_border_style_annotations',
                                u"""Choose the border style for annotations """),
            label = _(u'label_border_style_annotations', u'Border Style for Annotations'),
            format='select',
            ),
        ),
    StringField(
        'borderWidth',
        schemata ='borders',
        required=1,
        widget=StringWidget(
            description = _(u'description_border_width',
                                u"""Choose the border width in px"""),
            label = _(u'label_border_width', u'Border Width'),
            ),
        ),
    BooleanField(
        'overloadBody',
        schemata ='plone-overloads',
        default = True,
        widget=BooleanWidget(
            description = _(u'description_overload_body',
                                u"""Do you want to overload the body style ?"""),
            label = _(u'label_overload_body', u'Overload Body Style'),
            ),
        ),
    BooleanField(
        'overloadHTMLTags',
        schemata ='plone-overloads',
        default = True,
        widget=BooleanWidget(
            description = _(u'description_overload_html_tags',
                                u"""Do you want to overload content styles (classic html tags) ?"""),
            label = _(u'label_overload_html_tags', u'Overload HTML Tags Styles'),
            ),
        ),
    BooleanField(
        'overloadContent',
        schemata ='plone-overloads',
        default = True,
        widget=BooleanWidget(
            description = _(u'description_overload_content',
                                u"""Do you want to overload standard plone styles used for content ?"""),
            label = _(u'label_overload_content', u'Overload Various Content Styles'),
            ),
        ),
    BooleanField(
        'overloadSiteActions',
        schemata ='plone-overloads',
        default = True,
        widget=BooleanWidget(
            description = _(u'description_overload_site_actions',
                                u"""Do you want to overload site actions styles ?"""),
            label = _(u'label_overload_site_actions', u'Overload Site Actions Styles'),
            ),
        ),
    BooleanField(
        'overloadSearchBox',
        schemata ='plone-overloads',
        default = True,
        widget=BooleanWidget(
            description = _(u'description_overload_search_box',
                                u"""Do you want to overload search box styles ?"""),
            label = _(u'label_overload_search_box', u'Overload Search Box Styles'),
            ),
        ),
    BooleanField(
        'overloadGlobalSections',
        schemata ='plone-overloads',
        default = True,
        widget=BooleanWidget(
            description = _(u'description_overload_global_sections',
                                u"""Do you want to overload global sections buttons styles ?"""),
            label = _(u'label_overload_global_sections', u'Overload Global Sections Styles'),
            ),
        ),
    BooleanField(
        'overloadPersonalTools',
        schemata ='plone-overloads',
        default = True,
        widget=BooleanWidget(
            description = _(u'description_overload_personal_tools',
                                u"""Do you want to overload personal tools buttons styles (login, preferences ...) ?"""),
            label = _(u'label_overload_personal_tools', u'Overload Personals Tools Styles'),
            ),
        ),
    BooleanField(
        'overloadBreadcrumbs',
        schemata ='plone-overloads',
        default = True,
        widget=BooleanWidget(
            description = _(u'description_overload_breadcrumbs',
                                u"""Do you want to overload breadcrumbs styles ?"""),
            label = _(u'label_overload_breadcrumbs', u'Overload Breadcrumbs Styles'),
            ),
        ),
    BooleanField(
        'overloadFooter',
        schemata ='plone-overloads',
        default = True,
        widget=BooleanWidget(
            description = _(u'description_overload_footer',
                                u"""Do you want to overload footer styles ?"""),
            label = _(u'label_overload_footer', u'Overload Footer Styles'),
            ),
        ),
    BooleanField(
        'overloadSiteMap',
        schemata ='plone-overloads',
        default = True,
        widget=BooleanWidget(
            description = _(u'description_overload_site_map',
                                u"""Do you want to overload site map styles ?"""),
            label = _(u'label_overload_site_map', u'Overload Site Map Styles'),
            ),
        ),
    BooleanField(
        'overloadColumns',
        schemata ='plone-overloads',
        default = True,
        widget=BooleanWidget(
            description = _(u'description_overload_columns',
                                u"""Do you want to overload columns styles ?"""),
            label = _(u'label_overload_columns', u'Overload Columns Styles'),
            ),
        ),
    BooleanField(
        'overloadForms',
        schemata ='plone-overloads',
        default = True,
        widget=BooleanWidget(
            description = _(u'description_overload_forms',
                                u"""Do you want to overload forms styles ?"""),
            label = _(u'label_overload_forms', u'Overload Forms Styles'),
            ),
        ),
    BooleanField(
        'overloadPortlets',
        schemata ='plone-overloads',
        default = True,
        widget=BooleanWidget(
            description = _(u'description_overload_portlets',
                                u"""Do you want to overload portlets styles ?"""),
            label = _(u'label_overload_portlets', u'Overload Portlets Styles'),
            ),
        ),
    BooleanField(
        'overloadCalendar',
        schemata ='plone-overloads',
        default = True,
        widget=BooleanWidget(
            description = _(u'description_overload_calendar',
                                u"""Do you want to overload calendar styles ?"""),
            label = _(u'label_overload_calendar', u'Overload Calendar Styles'),
            ),
        ),

    BooleanField(
        'overloadNavtree',
        schemata ='plone-overloads',
        default = True,
        widget=BooleanWidget(
            description = _(u'description_overload_navtree',
                                u"""Do you want to overload navigation tree styles (impact sitemap + navtree portlet) ?"""),
            label = _(u'label_overload_navtree', u'Overload Navigation Tree Styles'),
            ),
        ),
    BooleanField(
        'overloadAuthoring',
        schemata ='plone-overloads',
        default = True,
        widget=BooleanWidget(
            description = _(u'description_overload_authoring',
                                u"""Do you want to overload authoring styles (content views, actions etc ...) ?"""),
            label = _(u'label_overload_authoring', u'Overload Authoring Styles'),
            ),
        ),

    ), marshall=RFC822Marshaller())
