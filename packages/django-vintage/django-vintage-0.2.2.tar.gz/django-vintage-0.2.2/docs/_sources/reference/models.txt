===============
Model Reference
===============

.. contents::
   :depth:  1
   :local:
   :backlinks: top

ArchivedPage
============

.. py:class:: ArchivedPage

   An full or partial HTML page archived for posterity

   .. py:attribute:: url

      **Required** ``CharField(255)`` *Unique*

      The URL path used now. You will likely configure this to be behind a prefix, like in :ref:`setting-it-up`. Based on that example, if the URL value was ``/my/formerly/awesome/page.html``, the full URL would be: ``http://example.com/archive/my/formerly/awesome/page.html``

   .. py:attribute:: original_url

      **Required** ``CharField(255)``

      The full original URL. This is important for rewriting the internal references to other resources. Django Vintage will rewrite links to other archived documents, if they've been archived, or the full URL if they don't. It will also archive images and rewrite their URLs.

   .. py:attribute:: title

      ``CharField(200)``

      The page title, typically from the ``<title>`` tag.

   .. py:attribute:: content

      ``TextField``

      The content of the archived page. ``content`` can be any text. The ``content`` field is pre-rendered, as it stores links to other archived items using ``{% url %}`` and ``{{ STATIC_URL }}`` template tags and variables. No context is included in the rendering.

   .. py:attribute:: template

      ``CharField(70)``

      The template to use when rendering this page. See :ref:`how-django-vintage-selects-the-template` for more information on template selection.

   .. py:attribute:: metadata

      ``ModelFormField(`` :ref:`metadata-form-setting` ``)``

      The ``metadata`` field is fundamentally a text field that stores ``JSON`` data. The data stored is flexible and determined via a :py:class:`Form` set in :ref:`metadata-form-setting`.

   .. py:method:: relative_to_full_url

      :param str url: A relative, full or fully-qualified URL.
      :returns: A fully-qualified URL

      This method converts a URL into a fully-qualified URL. Some internal methods use it to determine if a reference matches the ``original_url`` of any archived resource.

   .. py:method:: get_links

      :returns: All the ``href`` attributes of every ``<a>`` tag in the content.
      :rtype: A ``list`` of ``str``

      A simple shortcut to get all the links referenced in the document. Links to other archived documents are formatted as ``{% url vintage_detail url=/url/path/ %}``

   .. py:method:: get_external_links

      :returns: All the ``href`` attributes of every ``<a>`` tag in the content that references an external resource.
      :rtype: A ``list`` of ``str``

      A simple shortcut to get all the external links referenced in the document. Very useful in deciding if there are more pages to archive.

   .. py:method:: update_links

      :param bool save: **Default:** ``True``. Should you save the results.
      :returns: ``None``

      Parse through the saved document and convert any external links that match an ``original_url`` to an internal reference.

      By default, it will save the updated content. The :py:meth:`save` method calls this every save.

   .. py:method:: update_images

      :param bool save: **Default:** ``True``. Should you save the results.
      :returns: ``None``

      Parse through the saved document and convert any external ``<img>`` sources into :py:class:`ArchivedFile` objects and update the reference.

      By default, it will save the updated content. The :py:meth:`save` method calls this every save.

   .. py:method:: get_original_image

      :param str path: The URL of an image.
      :returns: The internal URL

      Retrieve an image referenced internally and create an :py:class:`ArchivedFile` object, unless the fully-qualified URL matches the ``original_url`` of a ``ArchivedFile`` object.

   .. py:method:: save

      Each time an object is saved, the content is parsed for updates to links and images. If there isn't an ``id``, it is first saved, so new :py:class:`ArchivedFile`\ s have something to reference.


ArchivedFile
============

.. py:class:: ArchivedFile

   A non-html file used in an Archived Page, such as an image

   .. py:attribute:: archivedpage

      **Required** ``ForeignKey(`` :py:class:`ArchivedPage` ``)`` *Related Name:* ``files``

      The document in which this file is referenced.

   .. py:attribute:: original_url

      **Required** ``CharField(255)``

      The full original URL. This is important for rewriting the internal references to other resources.

   .. py:attribute:: content

      ``FileField``

      The file is stored in the :ref:`storage-setting` setting and uploaded to ``vintage/<archivedpage.id>``.
