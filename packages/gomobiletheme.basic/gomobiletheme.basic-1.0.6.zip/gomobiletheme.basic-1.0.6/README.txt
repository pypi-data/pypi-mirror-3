Introduction
============

This product provides *Go Mobile Default Theme*  
mobile site theme for `Go Mobile for Plone <http://webandmobile.mfabrik.com>`.
The theme look and feel resemble's Plone 4's `Sunburst <http://plone.org/products/plonetheme.sunburst>`_
theme.

The theme contains two optimized image resolutions

* 48x48 based icon tiles for > 640 pixels wide mobile screens
  (based on Javascript screen width detection).

* 24x24 based icon tiles for smaller screens

CSS3 styles are used for WebKit based mobile browsers.

Low-end phones, or non-webkit based proprietary mobile browsers,
are also supported partially.

Developer notes
----------------

Icons
======

All action icons are in ``artwork`` folder,  including
Inkscape SVG orignals.  

Social media icons
==================

Theme also includes some popular social media icons

* Facebook

* Twitter

* mFabrik

All social media icons have only one version 32 x 32.

Buttons
=======
All buttons are in the same file as layers,
so you can easily do semi-automatic batch exports
for them with different sizes from Inkscape. 


Plone 3 compatibility changes
=============================

``gomobiletheme.basic`` codebase contains branching,
either in Python code or on a ``gomobiletheme_plone3``
skin layer to maintain Plone 3 backwards compatibility.

* search.pt customizations only for Plone 4

* batch_macros.pt customizations only for Plone 4

* Top site action links only for Plone 4

* <head> has some conditions to include Plone 4 specific stuff

* Plone 3 compatible main_template.pt

* Plone 3 compatible search.pt

Author
------

`mFabrik Research Oy <mailto:research@mfabrik.com>`_ - Python and Plone professionals for hire.

* `Web and mobile project - mobilize your Plone site in an instant <http://webandmobile.mfabrik.com>`_

* `mFabrik web site <http://mfabrik.com>`_ 

* `mFabrik mobile site <http://mfabrik.mobi>`_ 

* `Blog <http://blog.mfabrik.com>`_

* `More about Plone <http://mfabrik.com/technology/technologies/content-management-cms/plone>`_ 


