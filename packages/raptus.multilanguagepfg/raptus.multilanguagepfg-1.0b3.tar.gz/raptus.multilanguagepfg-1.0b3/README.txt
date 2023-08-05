Introduction
============

Provides integration of raptus.multilanguagefields.

The following features for raptus.article are provided by this package:

Fields
------
    * Use raptus.multilanguagefields for PloneFormGen 
    
Dependencies
------------
    * raptus.multilanguageplone

Installation
============

To install raptus.multilanguagepfg into your Plone instance, locate the file
buildout.cfg in the root of your Plone instance directory on the file system,
and open it in a text editor.

Add the actual raptus.article.multilanguagefields add-on to the "eggs" section of
buildout.cfg. Look for the section that looks like this::

    eggs =
        Plone

Next step is to add the zcml files to the "zcml" section of buildout.cfg. Look for the section that looks like this::

    zcml =
        raptus.multilanguagepfg

Note that you have to run buildout like this::

    $ bin/buildout

Usage
=====

Use multilanguagepfg
----------------------
Now edit PloneFormGen. You will get for each field the possibility to translate.

Copyright and credits
=====================

raptus.multilanguagepfg is copyrighted by `Raptus AG <http://raptus.com>`_ and licensed under the GPL. 
See LICENSE.txt for details.
