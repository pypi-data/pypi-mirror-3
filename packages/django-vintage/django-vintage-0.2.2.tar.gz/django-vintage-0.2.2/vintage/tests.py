from django.test import TestCase
from django.test.client import RequestFactory

from .models import ArchivedPage

HTML_RESULT = "<html><head><title>My test page</title></head><body>" \
    "<b>This is my test page</b><p>1234</p>" \
    "<p>There is no way to describe this</p><p>/path/to/my/image.png</p>" \
    "<p>test,testing,1,2,3</p><p>Testy McTestican</p></body></html>"


class vintageTest(TestCase):
    """
    Tests for django-vintage
    """
    def setUp(self):
        self.request_factory = RequestFactory()

    def createPage(self):
        return ArchivedPage(
            url='/test/',
            title='My test page',
            content='<b>This is my test page</b>',
            template_name='vintage/test.html',
            metadata={
                'page_id': '1234',
                'image': '/path/to/my/image.png',
                'description': 'There is no way to describe this',
                'keywords': 'test,testing,1,2,3',
                'author': 'Testy McTestican',
            }
        )

    def testCreation(self):
        """
        Create a basic ArchivedPage object
        """
        pg = self.createPage()
        pg.save()
        self.assertEquals(pg.url, '/test/')
        self.assertEquals(pg.title, 'My test page')
        self.assertEquals(pg.content, '<b>This is my test page</b>')
        self.assertEquals(pg.template_name, 'vintage/test.html')
        self.assertEquals(pg.metadata['page_id'], '1234')
        self.assertEquals(pg.metadata['image'], '/path/to/my/image.png')
        self.assertEquals(pg.metadata['description'], 'There is no way to describe this')
        self.assertEquals(pg.metadata['keywords'], 'test,testing,1,2,3')
        self.assertEquals(pg.metadata['author'], 'Testy McTestican')
        self.assertEquals(pg.get_absolute_url(), '/vintage/test/')

    def testTemplatePathCreation(self):
        """
        See if the template paths are getting created correctly
        """
        from .views import get_templates_from_path
        results = get_templates_from_path('/articles/2010/may/01/bigfoot-sighted/')
        expected = [
            '/vintage/articles/2010/may/01/bigfoot-sighted.html',
            '/vintage/articles/2010/may/01.html',
            '/vintage/articles/2010/may.html',
            '/vintage/articles/2010.html',
            '/vintage/articles.html',
        ]
        self.assertEqual(results[0], expected[0])
        self.assertEqual(results[1], expected[1])
        self.assertEqual(results[2], expected[2])
        self.assertEqual(results[3], expected[3])
        self.assertEqual(results[4], expected[4])

    def testView(self):
        """
        Make sure the view is returning things correctly
        """
        from .views import render_archivedpage
        pg = self.createPage()
        pg.save()

        url = 'test/'
        request = self.request_factory.get('/vintage/%s' % url)
        response = render_archivedpage(request, url)
        self.assertEquals(response.status_code, 200)
        self.assertEquals(response.content, HTML_RESULT)

    def testURL(self):
        pg = self.createPage()
        pg.save()

        response = self.client.get('/vintage/test/')
        self.assertEquals(response.status_code, 200)
        self.assertEquals(response.content, HTML_RESULT)
