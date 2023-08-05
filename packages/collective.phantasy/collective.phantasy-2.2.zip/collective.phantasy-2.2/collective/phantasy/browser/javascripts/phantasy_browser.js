// Phantasy Browser Widget
phantasybrowser_openBrowser = function(path, fieldName, at_url, fieldRealName)
{
    atrefpopup = window.open(path + '/@@phantasybrowser_popup?fieldName=' + fieldName + '&fieldRealName=' + fieldRealName +'&at_url=' + at_url,'referencebrowser_popup','toolbar=no,location=no,status=no,menubar=no,scrollbars=yes,resizable=yes,width=500,height=550');
}

referencebrowser_openBrowser = phantasybrowser_openBrowser;