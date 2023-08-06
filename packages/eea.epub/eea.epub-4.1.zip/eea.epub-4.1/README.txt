EEA Epub product
================
A product which allows you to import in Plone epub files.

Contents
========

.. contents::


Introduction
============

EEA Epub product allows you to import in Plone epub files. On upload,
Epub content will imported as Plone folders, files, images and documents.

Export to Epub is also available.

Note that only epub files created with "Adobe InDesign CS4" are supported for import.


Main features
=============

EEA Epub features:

  1. Import epub files as Plone content.
  2. Export into epub format.

EEA Epub makes the following assumptions:

  1. You don't use unicode or other special characters into the name of the epub, images or links
  2. You've created the epub with "Adobe InDesign CS4" which uses some standards for thr following:

    * The table of contents is named toc.ncx and is placed inside OEBPS
    * Book text & images are placed inside the folder OEBPS or other folders that are children of OEBPS
    * Items ids doesn't contain the following characters . / \ ( if possible stick to letters, numbers and - _ )

Best practices when creating an epub:

  1. Chapter names should not be all uppercase or use special characters
  2. Image names should not contain spaces, periods, / or other special characters

Epubs that were created with "Adobe inDesign CS4" but failed to upload:

  1. At this moment any errors that would appear on the site are surpressed by the info message: "An error occur during upload, your EPUB format may not be supported"
  2. If you've made the epub with "Adobe InDesign CS4" and yet you get this info message then please reopen this ticket and upload there the troubleing epub: https://svn.eionet.europa.eu/projects/Zope/ticket/3883

More details about how to use this package can be found at the following link:

  1. http://svn.eionet.europa.eu/projects/Zope/wiki/HowToEpub


Installation
============

The easiest way to get eea.epub support in Plone 4 using this
package is to work with installations based on `zc.buildout`_.
Other types of installations should also be possible, but might turn out
to be somewhat tricky.

To get started you will simply need to add the package to your "eggs" and
"zcml" sections, run buildout, restart your Plone instance and install the
"eea.epub" package using the quick-installer or via the "Add-on
Products" section in "Site Setup".

  .. _`zc.buildout`: http://pypi.python.org/pypi/zc.buildout/

You can download a sample buildout at:

  https://svn.eionet.europa.eu/repositories/Zope/trunk/eea.epub/buildouts

Getting started
===============

From "Add new" menu select "EpubFile" and upload an epub file.

Dependecies
===========

  1. Plone 4.x
  2. BeautifulSoup


Live demo
=========

Here some live production demos at EEA (European Environment Agency)

  1. http://www.eea.europa.eu/soer/synthesis


Source code
===========

Latest source code (Plone 4 compatible):
   https://svn.eionet.europa.eu/repositories/Zope/trunk/eea.epub/trunk

Plone 2 and 3 compatible:
   https://svn.eionet.europa.eu/repositories/Zope/trunk/eea.epub/branches/plone25


Copyright and license
=====================
The Initial Owner of the Original Code is European Environment Agency (EEA).
All Rights Reserved.

The EEA Epub (the Original Code) is free software;
you can redistribute it and/or modify it under the terms of the GNU
General Public License as published by the Free Software Foundation;
either version 2 of the License, or (at your option) any later
version.

More details under docs/License.txt


Links
=====

  1. EEA Epub wiki page: https://svn.eionet.europa.eu/projects/Zope/wiki/HowToEpub


Funding
=======

  EEA_ - European Enviroment Agency (EU)

.. _EEA: http://www.eea.europa.eu/
