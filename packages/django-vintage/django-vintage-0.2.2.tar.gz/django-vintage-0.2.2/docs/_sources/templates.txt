===============
Using templates
===============

.. contents::
   :depth:  1
   :local:
   :backlinks: top

Where they go
=============

Django Vintage looks for all of its templates within a directory named ``vintage``. Typically you will create this directory in your project's primary template directory, but as long as it is in one of your ``TEMPLATE_DIRS`` it should work.

The default template
====================

The default template is named ``default.html`` and should reside within the ``vintage`` directory.

Make your vintage default template extend from your project's base template. Override the appropriate blocks and insert the context variables so they render properly. Here is an example:

.. literalinclude:: includes/default_tmpl.html
   :language: django


.. _how-django-vintage-selects-the-template:

How Django Vintage selects the template
=======================================

Based on the URL of the requested page, it looks for the most specific to the most generic: For example, a vintage page with the the URL path: ``/articles/2010/may/01/bigfoot-sighted/`` would look for the following templates, in order:

1. /vintage/articles/2010/may/01/bigfoot-sighted.html
2. /vintage/articles/2010/may/01.html
3. /vintage/articles/2010/may.html
4. /vintage/articles/2010.html
5. /vintage/articles.html
6. /vintage/default.html

The template context
====================

The context for the template contains only ``object``.