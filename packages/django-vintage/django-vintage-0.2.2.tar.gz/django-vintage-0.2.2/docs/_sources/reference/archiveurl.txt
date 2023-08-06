=====================================
Importing a page with ``process_url``
=====================================

.. _process_url:

``process_url``
===============

.. py:method:: vintage.archiveurl.process_url

   :param str url: **Required** The URL to retrieve
   :param dict kwargs: Arguments for `BeautifulSoup` indicating which part of the document to return. If not otherwise specified, the ``<body>`` contents are returned.
   :rtype: ``list`` plus attribute ``metadata``
   :returns: A ``list`` of ``BeautifulSoup`` tags plus a ``dict`` of metadata. The metadata includes the contents of the ``<title>`` tag and ``<meta>`` tags. The keys for the ``<meta>`` data is the contents of its ``name`` or ``http-equiv`` attribute.


All kwargs are passed to BeautifulSoup's ``findAll`` method. Valid keyword args:

**name**
    Restricts the set of tags by name. examples::

        name='b'
        name=re.compile('^b')
        name=['title', 'p']
        name={'title': True, 'p': True}
        name=True  # this returns all tags. Useful when limiting by attrs
        name=lambda tag: len(tag.attrs) == 2

**attrs**
    A dictionary that acts just like the BeautifulSoup keyword arguments,
    but works for situations where there are already function arguments with
    the same name (like ``name``), or are python keywords (like ``class``).

**recursive**
    Doesn't really have any effect as you are starting from the top

**text**
    Lets you search for ``NavigableString`` objects instead of ``Tags``\ . Its
    value can be a string, a regular expression, a list or dictionary,
    True or None, or a callable that takes a NavigableString object as its
    argument

**limit**
    Stop after finding this many elements

Any other keyword arguments impose restrictions on ``Tag`` attributes.

The ``list`` returned also includes a ``metadata`` dictionary. This attribute aggregates all the metadata information from the page ``<head>``. The ``<title>`` is included under the key ``title`` and any ``<meta>`` tags it finds. The metadata dictionary uses either the ``name`` attribute or ``http-equiv`` attribute of the ``<meta>`` tag for the key and the ``content`` attribute for the value.
