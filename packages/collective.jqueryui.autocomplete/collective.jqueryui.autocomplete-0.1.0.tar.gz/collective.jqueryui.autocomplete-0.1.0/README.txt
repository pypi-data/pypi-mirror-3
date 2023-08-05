.. contents::

Introduction
============

Add to your Plone site the minimal code needed to have the `jQueryUI Autocomplete`__ feature.

__ http://jqueryui.com/demos/autocomplete/

This product is targeted on developers. This simply add to Plone a new JavaScript source and
the basical CSS needed to see a pretty autocomplete dropdown.

Warnings
========

When you DON'T need this
------------------------

You **must not** install this product if your Plone site already have other jQueryUI products like:

* `collective.js.jqueryui`__ (the most common)
* `collective.javascript.jqueryui`__
* ...others?

__ http://pypi.python.org/pypi/collective.js.jqueryui
__ http://pypi.python.org/pypi/collective.javascript.jqueryui

All products above have some drawbacks. For example latest ``collective.js.jqueryui`` doesn't play well with
Plone 3 (and the Plone 3 compatible version doesn't include autocomplete plugin yet).

On the other hand ``collective.javascript.jqueryui`` cleaner but don't register any resource.

When you need this
------------------

You need to use jQueryUI autocomplete but you don't want to include the whole jQueryUI stuff that products
above give you.

Authors
=======

This product was developed by RedTurtle Technology team.

.. image:: http://www.redturtle.it/redturtle_banner.png
   :alt: RedTurtle Technology Site
   :target: http://www.redturtle.it/
