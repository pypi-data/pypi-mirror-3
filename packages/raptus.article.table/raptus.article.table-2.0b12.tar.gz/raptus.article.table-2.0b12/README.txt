Introduction
============

You have a site where you have a lot of tables to be displayed and styled, then this
package is for you. It provides a generic way to create tables in articles.

The following features for raptus.article are provided by this package:

Content
-------
    * Provides a table content type for raptus.article

Components
----------
    * raptus.article.table.right
    * raptus.article.table.left
    * raptus.article.table.full

Dependencies
------------
    * archetypes.schemaextender
    * raptus.article.core

Installation
============

To install raptus.article.table into your Plone instance, locate the file
buildout.cfg in the root of your Plone instance directory on the file system,
and open it in a text editor.

Add the actual raptus.article.table add-on to the "eggs" section of
buildout.cfg. Look for the section that looks like this::

    eggs =
        Plone

This section might have additional lines if you have other add-ons already
installed. Just add the raptus.article.table on a separate line, like this::

    eggs =
        Plone
        raptus.article.table

Note that you have to run buildout like this::

    $ bin/buildout

Then go to the "Add-ons" control panel in Plone as an administrator, and
install or reinstall the "raptus.article.default" product.

Note that if you do not use the raptus.article.default package you have to
include the zcml of raptus.article.table either by adding it
to the zcml list in your buildout or by including it in another package's
configure.zcml.

Usage
=====

Add table
---------
You may now add tables in your article. Click the "Add new" menu and select "Table" in the pull down menu.
You get the standard plone form to add your table.

Configure your table
--------------------
Tables consist of a fixed column definition which may be set either per table or
globally in the table configlet. Every table needs either a global definition or 
a local one to work.

Components
----------
Navigate to the "Components" tab of your article, select one of the table components
and press "save and view". Note that at least one table has to be contained
in the article in which this component is active.

Copyright and credits
=====================

raptus.article is copyrighted by `Raptus AG <http://raptus.com>`_ and licensed under the GPL. 
See LICENSE.txt for details.
