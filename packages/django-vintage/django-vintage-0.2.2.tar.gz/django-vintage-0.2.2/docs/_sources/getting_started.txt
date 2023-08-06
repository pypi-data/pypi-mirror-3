===============
Getting Started
===============

.. contents::
   :depth:  1
   :local:
   :backlinks: top


Installation
============

Installation is easy using ``pip``.

.. code-block:: bash

    pip install django-vintage

Then add ``'vintage'`` to ``INSTALLED_APPS`` in your project's ``settings.py``


.. _setting-it-up:

Setting it up
=============

#. Create an entry in your ``urls.py`` for all your archived pages:

    .. code-block:: python

        urlpatterns = patterns('',
            # ...
            (r'^archive/', include('vintage.urls')),
            # ...
        )


#. Create a directory called ``vintage`` in your template directory

#. Create a new template called ``default.html`` in that directory

#. The template receives an ``object`` context variable that contains the :py:class:`ArchivedPage` instance. Here's a basic example:

   .. literalinclude:: includes/default_tmpl.html
      :linenos:
      :language: django



Creating a page manually
========================

#. Click on the new page button in the admin.

#. Enter the URL path of the old page. Should be everything after the http://domainname.com. For Example: ``/articles/2010/may/01/bigfoot-sighted/``.

#. Enter the page's title.

#. Enter the original URL of the page. The original URL is used in updating links and images.

#. View the source of the page you are archiving.

#. Select the appropriate HTML content (such as everything between the ``<body>`` tags).

#. Paste it into the content field.

#. Select a template (leave blank for default) see :ref:`How Django Vintage selects the template<how-django-vintage-selects-the-template>`

#. Enter in any of the page's metadata fields: ``page_id``, ``image``, ``description``, ``keywords``, and ``author``.


Importing a page programatically
================================

Django Vintage provides a method of retreiving a URL and saving it and the files to which it links. The example code below reads URLs from a file and extracts a specific part of the document. Then it runs it through a function to strip out additional parts of the document it doesn't want, such as copyright information that is already in the template, and ``form``\ s and ``script``\ s. See :ref:`process_url` for more information.

.. literalinclude:: includes/demo_import.py
   :linenos:
