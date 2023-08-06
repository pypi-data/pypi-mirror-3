from urllib2 import urlopen, URLError
from BeautifulSoup import BeautifulSoup


def process_url(url, **kwargs):
    """
    Retrieve the URL and optionally return back part of it using BeautifulSoup

    All kwargs are passed to BeautifulSoup's findAll method. Valid keyword args:

    name: restricts the set of tags by name. examples:
        name='b'
        name=re.compile('^b')
        name=['title', 'p']
        name={'title': True, 'p': True}
        name=True  # this returns all tags. Useful when limiting by attrs
        name=lambda tag: len(tag.attrs) == 2
    attrs: a dictionary that acts just like the BeautifulSoup keyword arguments,
        but works for situations where there are already function arguments with
        the same name (like ``name``), or are python keywords (like ``class``).
    recursive: Doesn't really have any effect as you are starting from the top
    text: lets you search for NavigableString objects instead of Tags. Its
        value can be a string, a regular expression, a list or dictionary,
        True or None, or a callable that takes a NavigableString object as its
        argument
    limit: stop after finding this many elements
    Any other keyword arguments impose restrictions on tag attributes.
    """
    try:
        html = urlopen(url).read()
    except URLError, e:
        print "Couldn't get %s due to %s" % (url, e)

    soup = BeautifulSoup(html)
    metadata = {}
    for tag in soup.head.contents:
        if hasattr(tag, 'name'):
            if tag.name == 'title':
                metadata['title'] = tag.string
            elif tag.name == 'meta':
                if tag.haskey('name'):
                    metadata[tag['name']] = tag['content']
                else:
                    metadata[tag['http-equiv']] = tag['content']
    if kwargs:
        if 'name' not in kwargs:
            kwargs['name'] = None
        result = soup.findAll(**kwargs)
    else:
        # Of course, we could use soup.body, but we use the same form as above
        # consistency
        result = soup.findAll('body', limit=1)
    result.metadata = metadata.copy()
    return result
