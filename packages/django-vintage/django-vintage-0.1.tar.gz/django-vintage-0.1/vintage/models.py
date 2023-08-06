from __future__ import unicode_literals

import os

from django.db import models
from django.utils.translation import ugettext_lazy as _
# from django.contrib.contenttypes import generic

from .settings import METADATA_FORM, STORAGE
from .compatible import ModelFormField
# from genericm2m.models import RelatedObjectsDescriptor


class ArchivedPage(models.Model):
    """
    Part of an HTML page
    """
    url = models.CharField(
        _('URL'),
        max_length=255,
        db_index=True,
        unique=True)
    original_url = models.CharField(
        _('original URL'),
        max_length=255)
    title = models.CharField(
        _('title'),
        blank=True,
        max_length=200)
    content = models.TextField(
        _('content'),
        blank=True)
    template_name = models.CharField(
        _('template name'),
        max_length=70,
        blank=True,
        help_text=_("""Example: 'vintage/contact_page.html'. If this
            isn't provided, the system will use 'vintage/default.html'."""))
    metadata = ModelFormField(METADATA_FORM)

    # related = RelatedObjectsDescriptor()

    class Meta:
        verbose_name = _('archived page')
        verbose_name_plural = _('archived pages')
        ordering = ('url',)

    def __unicode__(self):
        return "%s -- %s" % (self.url, self.title)

    @models.permalink
    def get_absolute_url(self):
        return ('vintage_detail', (), {'url': self.url.lstrip('/')})

    def relative_to_full_url(self, url):
        """
        Resolve the URL based on the object's original_url
        """
        from urllib2 import urlparse
        parsed = urlparse.urlparse(url)
        if not parsed.netloc:
            url = urlparse.urljoin(self.original_url, parsed.path)
        return url

    def get_links(self):
        """
        Return all the hrefs of all the <a> tags in the content
        """
        from BeautifulSoup import BeautifulSoup

        soup = BeautifulSoup(self.content)
        links = soup.findAll('a')
        hrefs = [tag['href'] for tag in links if tag.has_key('href')]
        return hrefs

    def get_external_links(self):
        """
        Update all the links, and then return any URL that is external
        """
        self.update_links(save=True)
        links = self.get_links()
        return [i for i in links if i.startswith('http')]

    def update_links(self, save=True):
        """
        Parse through the saved document and make sure the links to the existing
        site are archived.
        """
        from BeautifulSoup import BeautifulSoup

        soup = BeautifulSoup(self.content)
        links = soup.findAll('a')
        for tag in links:
            if not tag.has_key('href'):
                continue

            href = tag['href'].strip()
            if href.startswith('{'):
                continue
            if href.startswith('javascript'):
                continue
            url = self.relative_to_full_url(href)
            try:
                ap = ArchivedPage.objects.get(original_url=url)
                url = "{%% url vintage_detail url=%s %%}" % ap.url
            except ArchivedPage.DoesNotExist:
                pass
            tag['href'] = url
        self.content = str(soup.prettify())
        if save:
            self.save()

    def update_images(self, save=True):
        """
        Parse through the saved document and make sure the images are archived.
        """
        from BeautifulSoup import BeautifulSoup

        soup = BeautifulSoup(self.content)
        images = soup.findAll('img')
        for tag in images:
            src = tag['src'].strip()
            if not src.startswith('{'):
                url = self.get_original_image(src)
                tag['src'] = url
        self.content = str(soup.prettify())
        if save:
            self.save()

    def get_original_image(self, path):
        """
        Given a full or partial path, download and create the archivedfile.
        Return the url path instance
        """
        from urllib2 import urlopen, URLError, urlparse
        from django.core.files.base import ContentFile
        parsed = urlparse.urlparse(path.strip())
        path = self.relative_to_full_url(path.strip())
        try:
            af = ArchivedFile.objects.get(original_url=path)
        except ArchivedFile.DoesNotExist:
            try:
                file_content = urlopen(path).read()
                af = ArchivedFile(original_url=path)
                af.save()
                af.content.save(os.path.basename(parsed.path), ContentFile(file_content))
            except URLError:
                return path
        self.files.add(af)
        return '{{ STATIC_URL }}%s' % af.content.url

    def save(self, *args, **kwargs):
        if not self.id:
            super(ArchivedPage, self).save(*args, **kwargs)
        self.update_images(save=False)
        self.update_links(save=False)
        super(ArchivedPage, self).save(*args, **kwargs)


def get_upload_path(instance, filename):
    """
    Return the path based on the primary_key of the related page
    """
    from urlparse import urlparse
    parsed = urlparse(instance.original_url)
    directory_name = os.path.normpath(
        os.path.join(
            'vintage',
            parsed.netloc,
            os.path.dirname(parsed.path).strip('/'))
    )
    new_filename = os.path.normpath(
        instance.content.storage.get_valid_name(
            os.path.basename(filename)))
    return os.path.join(directory_name, new_filename)


class ArchivedFile(models.Model):
    """
    A non-html file used in an Archived Page, such as a file
    """
    archivedpages = models.ManyToManyField(ArchivedPage, related_name='files')
    original_url = models.CharField(
        _('original URL'),
        max_length=255,
        unique=True)
    content = models.FileField(
        max_length=255,
        upload_to=get_upload_path,
        storage=STORAGE())
