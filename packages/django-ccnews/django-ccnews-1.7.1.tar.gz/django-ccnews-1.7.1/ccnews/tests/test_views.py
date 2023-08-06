from datetime import datetime
from django.test import TestCase
from django.core.urlresolvers import reverse
from ccnews.views import index, month, view
from ccnews.tests.mock import MockRequest
from ccnews.models import Article


class ViewTestCases(TestCase):

    def setUp(self):
        self.rf = MockRequest()

    def test_month_valid_dates(self):
        """The month requires valid arguments for datetime"""
        response = self.client.get(reverse(
                        'ccnews:month',
                        args=[2012,25]))
        self.assertEqual(404, response.status_code)

    def test_index_200(self):
        """The index page responds with a 200 ok"""
        request = self.rf.get(reverse('ccnews:index'))
        response = index(request)
        self.assertEqual(200, response.status_code)

    def test_month_200(self):
        """The month page responds with a 200 ok"""
        # make article 1
        a1 = Article()
        a1.title = '1'
        a1.slug = '1'
        a1.content = '1111111'
        a1.status = Article.VISIBLE
        a1.created = datetime(year=2012, month=5, day=19)
        a1.save()
        request = self.rf.get(reverse(
                        'ccnews:month',
                        args=[2012,05]))
        response = month(request, 2012, 05)
        self.assertEqual(200, response.status_code)

    def test_month_404(self):
        """The month page responds with a 404 not found
        if there are no articles for that month"""
        # make a page
        response = self.client.get(reverse(
                        'ccnews:month',
                        args=[2012,05]))
        self.assertEqual(404, response.status_code)

    def test_view_200(self):
        """The index page responds with a 200 ok"""
        # make article 1
        a1 = Article()
        a1.title = '1'
        a1.slug = '1'
        a1.content = '1111111'
        a1.status = Article.VISIBLE
        a1.created = datetime(year=2012, month=5, day=19)
        a1.save()
        request = self.rf.get(reverse(
                        'ccnews:view',
                        args=[2012,05,'1']))
        response = view(request, 2012, 5, 1)
        self.assertEqual(200, response.status_code)

    def test_view_404(self):
        """The view page responds with a 404 not found
        if there is no article for that slug"""
        # make a page
        response = self.client.get(reverse(
                        'ccnews:view',
                        args=[2012,05,'1']))
        self.assertEqual(404, response.status_code)
