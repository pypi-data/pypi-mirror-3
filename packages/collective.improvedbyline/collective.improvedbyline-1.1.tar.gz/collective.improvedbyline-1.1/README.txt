Introduction
============

This package extends standard ``Plone`` byline viewlet with publication date.


Overview
--------

This is how this enhanced byline viewlet works. In case object is published then
publication date is displayed: ``published <date>``. If object is not published
then only modification date shows up: ``last modified <date>``. In case object
is published and modified afterwards then both dates appear in byline viewlet:
``published <date>, last modified <date>``.

All other byline elements left intact.


Compatibility
-------------

This add-on was tested in Plone 4.0.


Installation
------------

* to add the package to your Zope instance, please, follow the instructions found inside the
  ``docs/INSTALL.txt`` file
* then restart your Zope instance and install the ``collective.improvedbyline``
  package from within the ``portal_quickinstaller`` tool

To remove viewlet from your site simply uninstall ``collective.improvedbyline``
package from within the ``portal_quickinstaller`` tool.
