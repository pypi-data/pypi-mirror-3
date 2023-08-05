Introduction
============

Provides a maps content type to be added to articles

The following features for raptus.article are provided by this package:

Content
-------
    * Map - add google maps in an article.
    * Marker - add markers in a map.

Components
----------
    * Maps (List of maps contained in the article over the whole width.)
    * Maps left (List of maps contained in the article on the left side.)
    * Maps right (List of maps contained in the article on the right side.)

Dependencies
------------
    * raptus.googlemaps
    * raptus.article.core

Installation
============

To install raptus.article.maps into your Plone instance, locate the file
buildout.cfg in the root of your Plone instance directory on the file system,
and open it in a text editor.

Add the actual raptus.article.maps add-on to the "eggs" section of
buildout.cfg. Look for the section that looks like this::

    eggs =
        Plone

This section might have additional lines if you have other add-ons already
installed. Just add the raptus.article.maps on a separate line, like this::

    eggs =
        Plone
        raptus.article.maps

Note that you have to run buildout like this::

    $ bin/buildout

Then go to the "Add-ons" control panel in Plone as an administrator, and
install or reinstall the "raptus.article.default" product.

Note that if you do not use the raptus.article.default package you have to
include the zcml of raptus.article.maps either by adding it
to the zcml list in your buildout or by including it in another package's
configure.zcml.

Usage
=====

Add map
-------
You may now add maps in your article. Click the "Add new" menu and select "Map" in the pull down menu.
You get the standard plone form to add your map. 

Components
----------
Navigate to the "Components" tab of your article, select the map component
and press "save and view". Note that at least one map has to be contained
in the article in which this component is active.

Copyright and credits
=====================

raptus.article is copyrighted by `Raptus AG <http://raptus.com>`_ and licensed under the GPL. 
See LICENSE.txt for details.
