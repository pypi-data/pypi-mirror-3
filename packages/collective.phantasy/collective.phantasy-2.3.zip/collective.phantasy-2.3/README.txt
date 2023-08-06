Introduction :
==============

Change the skin of your plone site, change the skin of any content based on ATFolder on the site,
using a simple form.

Just Upload images with the same name in the skin using a tgz or a zip,
to overload standard plone skin images referenced in css.

You can add a css for each skin.

You can choose to overload, all parts, or just some parts, of the plone standard css.

You can change Logo, Footer or Colophon viewlets using phantasy skin edit form.

You can choose to display or not plone standard dynamic viewlets (searchbox, site actions ...)

The viewlets configuration is taken from the first skin associated with a parent object.

The css are taken from all skins associated with all parents.

The static viewlets edition could be more easy for users if Products.FCKeditor
is installed in Plone (the FCKwidget is used).

You can add a favicon for each skin, uploading a favicon.ico file.

Dependencies :
==============

- Plone 4.0.x, Plone 4.1.x.

- archetypes.schemaextender
  (used to add a referencefield to standard Plone Folders)

- Products.SmartColorWidget

All dependencies are installed when using buildout or easy_install.

Installation :
==============

read docs/INSTALL.txt inside product to install it in your Zope instance

Then in your Plone Site, use portal_quick_installer to install it in Plone,
this will also install Products.SmartColorWidget.


FAQ :
=====

* How to make my own phantasy config and css ?

  Just look at the aws.minisite package code, it's a complete example which will show
  you how to make a new skin schema and how to override phantasy css. In aws.minisite
  you will also find a way to use collective.phantasy with a different
  strategy (the schema extender field is no more used, instead, when
  creating a new "Mini Site" you are invited to choose a skin, and this skin is
  copied/pasted inside the Mini Site. Then the Mini Site owner is able
  to change the mini site skin by himself.)


ROADMAP :
=========

* Replace Archetypes Schema with a zope3 schema for skin data
  (no planning for now)

