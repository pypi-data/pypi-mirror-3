EEA Relations
=============
EEA Relations package redefines relations in Plone. Right now in Plone any
object can be in relation with any other object. EEA Relations lets you to
define possible relations between objects. EEA Relations also comes with a nice,
customizable faceted navigable popup for relations widget.


Contents
========

.. contents::


Introduction
============

Once installed from "Add-ons", the package will add an utility
called "Possible relations" under control panel.


Main features
=============

Main goal of EEA Relations is to be an alternative to the default Plone
related item widget.

EEA Relations features:

  1. Define/restrict what kind of content types a certain content can relate to
  2. Set restrictions on possible relations (e.g. relations can be made
     only with published content)
  3. You can define easy to use faceted searches (using EEA Faceted navigation)
     on the relate items popup
  4. Nice visual diagram showning all the relations and restrictions you defined
     (Control pane -> Possible relations)

Installation
============

The easiest way to get eea.relations support in Plone 4 using this package is to
work with installations based on `zc.buildout`_.  Other types of installations
should also be possible, but might turn out to be somewhat tricky.

To get started you will simply need to add the package to your "eggs" and
"zcml" sections, run buildout, restart your Plone instance and install the
"eea.relations" package using the quick-installer or via the "Add-on
Products" section in "Site Setup".

  .. _`zc.buildout`: http://pypi.python.org/pypi/zc.buildout/

You can download a sample buildout at:

  http://svn.eionet.europa.eu/repositories/Zope/trunk/eea.relations/buildouts/plone4/


Getting started
===============

Once you install the package from control panel "Add-ons", the package will add
an utility called "Possible relations" under control panel from where you can start
define the relations, the constraints between contents etc.


Dependencies
============

  * graphviz

      yum install graphviz

      apt-get install graphviz


API Doc
=======

  http://apidoc.eea.europa.eu/eea.relations-module.html


Source code
===========

Latest source code (Plone 4 compatible):
   https://svn.eionet.europa.eu/repositories/Zope/trunk/eea.relations/trunk

Plone 2 and 3 compatible:
   https://svn.eionet.europa.eu/repositories/Zope/trunk/eea.relations/branches/plone25


Copyright and license
=====================
The Initial Owner of the Original Code is European Environment Agency (EEA).
All Rights Reserved.

The EEA Relations (the Original Code) is free software;
you can redistribute it and/or modify it under the terms of the GNU
General Public License as published by the Free Software Foundation;
either version 2 of the License, or (at your option) any later
version.

More details under docs/License.txt


Funding
=======

  EEA_ - European Enviroment Agency (EU)

.. _EEA: http://www.eea.europa.eu/
