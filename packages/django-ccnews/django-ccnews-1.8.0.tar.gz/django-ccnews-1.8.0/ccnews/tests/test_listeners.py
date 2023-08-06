import os
from unittest import skipUnless
from datetime import datetime
from django.test import TestCase
from django.conf import settings
from django.core.files import File
from ccnews import settings as c_settings
from ccnews.models import Article, ArticleAttachment

class ListenerTestCases(TestCase):

    # do a skipunless file exists on this one
    @skipUnless(os.path.exists('%s/ccnews/test.pdf' % settings.STATIC_ROOT),
            'test.pdf file does not exist')
    def test_title(self):
        """A title is set on a file from filename is none is supplied"""
        # open file
        test_pdf = open('%s/ccnews/test.pdf' % settings.STATIC_ROOT)
        # make page and attachment
        a1 = Article()
        a1.title = '1'
        a1.slug = '1'
        a1.content = '# hello world of tests'
        a1.status = Article.VISIBLE
        a1.created = datetime(year=1970, month=1, day=2)
        a1.save()
        at1 = ArticleAttachment()
        at1.article = a1
        at1.src = File(test_pdf, 'ccnews/test.pdf')
        at1.save()
        # the title is 'test.pdf'
        self.assertEqual(at1.title, 'test.pdf')
        test_pdf.close()
        os.unlink(at1.src.path)
        # make another one, but this time with a title
        test_pdf = open('%s/ccnews/test.pdf' % settings.STATIC_ROOT)
        at2 = ArticleAttachment()
        at2.article = a1
        at2.src = File(test_pdf, 'ccnews/test.pdf')
        at2.title = 'Arther'
        at2.save()
        # title is now arther
        self.assertEqual(at2.title, 'Arther')
        # delete the files
        test_pdf.close()
        os.unlink(at2.src.path)
  

    def test_excerpt(self):
        "The excerpt is correctly set and honours the config setting"""
        # set a very short length
        settings.CCNEWS_EXCERPT_LENGTH = 1
        reload(c_settings)
        a1 = Article()
        a1.title = '1'
        a1.slug = '1'
        a1.content = '# hello world of tests'
        a1.status = Article.VISIBLE
        a1.created = datetime(year=1970, month=1, day=2)
        a1.save()
        # we have one word in the excerpt
        self.assertEqual('hello ...', a1.excerpt)
        # remove our setting
        del(settings.CCNEWS_EXCERPT_LENGTH)
        reload(c_settings)
        # now we have the default length
        a1.save()
        self.assertEqual('hello world of tests', a1.excerpt)


    def test_content_rendered(self):
        """the content is rendered as markdown when an article
        is saved"""
        a1 = Article()
        a1.title = '1'
        a1.slug = '1'
        a1.content = '# hello'
        a1.status = Article.VISIBLE
        a1.created = datetime(year=1970, month=1, day=2)
        a1.save()
        # we have html
        self.assertHTMLEqual(
                '<h1 id="hello">hello</h1>',
                a1.content_rendered)

    def test_set_created(self):
        """a created date is set if none is supplied"""
        # make article 1
        a1 = Article()
        a1.title = '1'
        a1.slug = '1'
        a1.content = '1111111'
        a1.status = Article.VISIBLE
        a1.created = datetime(year=1970, month=1, day=2)
        a1.save()
        # make article 2
        a2 = Article()
        a2.title = '2'
        a2.slug = '2'
        a2.content = '2222222'
        a2.status = Article.HIDDEN
        a2.save()
        # both have dates
        self.assertTrue(a1.created)
        self.assertTrue(a2.created)
        # but a1 is 1970
        self.assertEqual(1970, a1.created.year)
        self.assertEqual(1, a1.created.month)
        self.assertEqual(2, a1.created.day)
