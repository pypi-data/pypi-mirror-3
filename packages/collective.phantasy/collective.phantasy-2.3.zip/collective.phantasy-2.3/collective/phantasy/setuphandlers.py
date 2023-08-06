from zope.app.component.hooks import getSite


def install_atphantasy_contents(context):

    if context.readDataFile('collective.phantasy_contents.txt') is None:
        return

    """install atphantasy skin structure"""
    portal = getSite()
    skinroot = {
                "type_name" : "PhantasySkin",
                "id" : "phantasy-root-skin",
                "title" : "Phantasy Root Skin",
               }
    skinroot_data = {
                "portalWidth" : "100%",
                "portalHorizontalPosition" : "0 auto 0 auto",
                "backgroundColor" : "#f6e9e9",
                "portalBackgroundColor" : "#ffffff",
                "evenRowBackgroundColor" : "#f6e9e9",
                "globalBackgroundColor" : "#f6e9e9",
                "globalFontColor" : "#7d3939",
                "globalBorderColor" : "#d8d8d8",
                "contentViewBackgroundColor" : "#f1d8d4",
                "contentViewFontColor" : "#820707",
                "contentViewBorderColor" : "#820707",
                "Language": "",
                }
    skinrepository = {"type_name" : "PhantasySkinsRepository",
                      "id" : "phantasy-skins-repository",
                      "title" : "Phantasy Skins Repository",
                      "Language": "",
                     }
    foldersample = {"type_name" : "Folder",
                    "id" : "folder-with-other-skin",
                    "title" : "Folder With Other Skin",
                   }
    skinsample = {
                  "type_name" : "PhantasySkin",
                  "id" : "phantasy-sample-skin",
                  "title" : "Phantasy Sample Skin",
                 }
    skinsample_data = {
                  "portalWidth" : "1000px",
                  "portalHorizontalPosition" : "0 auto 0 auto",
                  "backgroundColor" : "#e8deec",
                  "portalBackgroundColor" : "#ffffff",
                  "evenRowBackgroundColor" : "#e8deec",
                  "globalBackgroundColor" : "#e8deec",
                  "globalFontColor" : "#7d3939",
                  "globalBorderColor" : "#d8d8d8",
                  "contentViewBackgroundColor" : "#f1d8d4",
                  "contentViewFontColor" : "#820707",
                  "contentViewBorderColor" : "#820707",
                  "Language": "",
                  }
    if 'phantasy-root-skin' not in portal.objectIds() :
        portal.invokeFactory( **skinroot)
        o = getattr(portal, 'phantasy-root-skin')
        o.edit(**skinroot_data)

    if 'phantasy-skins-repository' not in portal.objectIds() :
        portal.invokeFactory( **skinrepository)
        o = getattr(portal, 'phantasy-skins-repository')
        o.invokeFactory( **skinsample)
        skin = getattr(o, 'phantasy-sample-skin')
        skin.edit(**skinsample_data)
        skinuid = skin.UID()
        if 'folder-with-other-skin' not in portal.objectIds() :
            portal.invokeFactory( **foldersample)
            o = getattr(portal, 'folder-with-other-skin')
            o.edit(local_phantasy_skin= skinuid)



