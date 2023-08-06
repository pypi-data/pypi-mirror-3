from urlparse import urlparse
from BeautifulSoup import BeautifulSoup
from vintage.archiveurl import process_url
from vintage.models import ArchivedPage, ArchivedFile

URLS = open(os.path.join(path, 'miscurls.txt')).readlines()

def post_process(main_content):
    for tag in main_content.contents:
        if hasattr(tag, 'name'):
            if tag.name == 'form':
                tag.extract()
            if tag.name == 'div' and tag.get('class', '') == 'emailthis':
                tag.extract()
            if tag.name == 'div' and tag.get('class', '') == 'copyright':
                tag.extract()
            if tag.name == 'script':
                tag.extract()
    return "".join([str(i) for i in main_content.contents])


for url in URLS:
    print "Archiving %s" % url
    initial_html = process_url(url, name="td", width="531", limit=1)
    metadata = initial_html.metadata.copy()
    html = post_process(initial_html[0])
    urlpath = urlparse(url).path.strip()
    ap = ArchivedPage(
        title=metadata.get('title', urlpath) or '',
        url=urlpath,
        original_url=url,
        content=html,
        metadata=metadata)
    ap.save()