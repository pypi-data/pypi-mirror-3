from django.shortcuts import render_to_response
from django.http import Http404, HttpResponsePermanentRedirect
from django.template import RequestContext
from django.shortcuts import get_object_or_404
from django.utils.safestring import mark_safe
from django.conf import settings
from django.template.loader import Template, Context

from .models import ArchivedPage

DEFAULT_TEMPLATE = 'vintage/default.html'


def get_templates_from_path(path):
    """
    Given a path like: /articles/2010/may/01/bigfoot-sighted/
    Create a list of paths like:
    1. /vintage/articles/2010/may/01/bigfoot-sighted.html
    2. /vintage/articles/2010/may/01.html
    3. /vintage/articles/2010/may.html
    4. /vintage/articles/2010.html
    5. /vintage/articles.html
    """
    bits = path.strip('/').split('/')
    templates = []
    for i in range(len(bits), 0, -1):
        templates.append('vintage/%s.html' % '/'.join(bits[:i]))
    return templates


def render_archivedpage(request, url):
    """
    Render a requested ArchivedPage URL
    """
    try:
        apage = get_object_or_404(ArchivedPage, url__exact="/%s" % url)
    except Http404:
        if not url.endswith('/') and settings.APPEND_SLASH:
            apage = get_object_or_404(ArchivedPage, url__exact="/%s/" % url)
            return HttpResponsePermanentRedirect('%s/' % request.path)
        else:
            raise
    if apage.template_name:
        templates = [apage.template_name, DEFAULT_TEMPLATE]
    else:
        templates = get_templates_from_path(url)
        templates.append(DEFAULT_TEMPLATE)

    # To avoid having to always use the "|safe" filter in flatpage templates,
    # mark the title and content as already safe (since they are raw HTML
    # content in the first place).
    apage.title = mark_safe(apage.title)
    apage.content = mark_safe(Template(apage.content).render(Context({})))

    return render_to_response(templates, {'object': apage}, RequestContext(request))
