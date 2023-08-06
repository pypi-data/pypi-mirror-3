====================
Customizing metadata
====================

So you want different fields of metadata, do you? That's easy enough. The metadata fields are controlled by the :ref:`metadata-form-setting`.

Creating the metadata form
==========================

There is no trick to the metadata form. It is a standard Django :py:class:`Form`. The default form looks like:

.. code-block:: python

    class MetadataForm(forms.Form):
        page_id = forms.CharField(required=False)
        title = forms.CharField(required=False)
        description = forms.CharField(required=False)
        image = forms.CharField(required=False)
        keywords = forms.CharField(required=False)
        author = forms.CharField(required=False)
