EEA Alchemy
===========
Auto-discover geographical coverage, temporal coverage and keywords from
documents common metadata (title, description, body, etc).


Contents
========

.. contents::


Introduction
============
This tool allows Plone managers to auto-discover and fix subject keywords,
location and temporal coverage using http://www.alchemyapi.com/ web service.


Main features
=============

- Auto-discover keywords, locations and temporal coverage


Planed features
===============

- Add a wizard icon near Subject, Location, etc fields in edit form
  to auto-discover and suggest tags based on text in
  other fields (Title, Description)


Installation
============

The easiest way to get eea.alchemy support in Plone 4 using this
package is to work with installations based on `zc.buildout`_.
Other types of installations should also be possible, but might turn out
to be somewhat tricky.

To get started you will simply need to add the package to your "eggs" and
"zcml" sections, run buildout, restart your Plone instance and install the
"eea.alchemy" package using the quick-installer or via the "Add-on
Products" section in "Site Setup".

  .. _`zc.buildout`: http://pypi.python.org/pypi/zc.buildout/

You can download a sample buildout at:

  https://svn.eionet.europa.eu/repositories/Zope/trunk/eea.alchemy/buildouts


Getting started
===============

1. Get your alchemy key here: http://www.alchemyapi.com/api/register.html
2. Update your alchemy API key within ZMI > Plone > portal_properties > alchemyapi
3. Within Plone Control panel go to Alchemy Tags.


Source code
===========

Latest source code (Plone 4 compatible):
   https://svn.eionet.europa.eu/repositories/Zope/trunk/eea.alchemy/trunk

Plone 2 and 3 compatible:
   https://svn.eionet.europa.eu/repositories/Zope/trunk/eea.alchemy/branches/plone25


Copyright and license
=====================
The Initial Owner of the Original Code is European Environment Agency (EEA).
All Rights Reserved.

The EEA Alchemy (the Original Code) is free software;
you can redistribute it and/or modify it under the terms of the GNU
General Public License as published by the Free Software Foundation;
either version 2 of the License, or (at your option) any later
version.

More details under docs/License.txt


Funding
=======

  EEA_ - European Enviroment Agency (EU)

.. _EEA: http://www.eea.europa.eu/
