.. contents::

Overview
========

Products.AROfficeTransforms is a Plone module to add conversion from office
format to HTML in portal_transforms tool


Introduction
============

This packages contains new portal_transforms. This version includes the
following transforms :

* MS Excel to html
* MS Word to html
* MS Word to text
* MS Powerpoint to html
* OpenOffice V1 (sxw, sxc, sxi) to html
* OpenOffice V2 / OASIS OpenDocument (odt, odc, odp) to html
* PDF to html
* Zip to Text

It is currently in production on GNU/Linux servers and needs the following
binaries :

* ppthtml
* xlhtml
* wv
* xsltproc
* unzip
* pdftohtml
* elinks | links | lynx


Time-consuming binaries
=======================

Sometimes, with .doc or .xls document, matching binaries happen to freeze or 
take to much time.
If the *timelimit* command is available in your system, this issue will be 
avoid. You can change the time-out value by setting your own WARNTIME and 
KILLTIME in the config.py file (defaults are 120 sec. and 10 sec.).
Thx to Thomas [thomasdesvenain] for this feature.

Authors
=======

|atreal|_

* `atReal Team`_

  - Thierry Benita [tbenita]
  - Jean-Nicolas Bes [drjnut]
  - Matthias Broquet [tiazma]
  - Florent Michon [f10w]

.. |atreal| image:: http://www.atreal.fr/medias/atreal-logo-48.png
.. _atreal: http://www.atreal.fr/
.. _atReal Team: mailto:contact@atreal.fr


Contributors
============

* [kdeldycke]
* [hpeteragitator]
* Thomas Desvenain [thomasdesvenain]
* Jean-Michel Francois [toutpt]
* [zegor]
*

