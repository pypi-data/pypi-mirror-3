from datetime import datetime
from django.conf import settings
from django.test import TestCase
from ccnews.models import Article
from ccnews import settings as c_settings

class ManagerTestCases(TestCase):

    def test_index(self):
        """Index returns only visible items and the total 
        amount returned is dependant on the value of
        c_settings.CCNEWS_INDEX_ITEMS"""
        # make article 1
        a1 = Article()
        a1.title = '1'
        a1.slug = '1'
        a1.content = '1111111'
        a1.status = Article.VISIBLE
        a1.created = datetime(year=2012, month=5, day=19)
        a1.save()
        # make article 2
        a2 = Article()
        a2.title = '2'
        a2.slug = '2'
        a2.content = '2222222'
        a2.status = Article.HIDDEN
        a2.created = datetime(year=2012, month=4, day=20)
        a2.save()
        # make article 3
        a3 = Article()
        a3.title = '3'
        a3.slug = '3'
        a3.content = '3333333'
        a3.status = Article.VISIBLE
        a3.created = datetime(year=2012, month=5, day=20)
        a3.save()
        # the default is ten, but we only have three, one is hidden
        self.assertEqual(2, Article.objects.index().count())
        # unhide the hidden and we have three
        a2.status = Article.VISIBLE
        a2.save()
        # now we have three
        self.assertEqual(3, Article.objects.index().count())
        # adjust the setting to 1
        settings.CCNEWS_INDEX_ITEMS = 1
        reload(c_settings)
        # now we have one
        self.assertEqual(1, Article.objects.index().count())
        # and it the latest one
        self.assertEqual(a3.pk, Article.objects.index()[0].pk)
        # remove the custom setting and reload

        del(settings.CCNEWS_INDEX_ITEMS)
        reload(c_settings)

    def test_nav_local(self):
        """test thati nav_local method behaves as expected"""
        # make article 1
        a1 = Article()
        a1.title = '1'
        a1.slug = '1'
        a1.content = '1111111'
        a1.status = Article.VISIBLE
        a1.created = datetime(year=2012, month=5, day=20)
        a1.save()
        # make article 2
        a2 = Article()
        a2.title = '2'
        a2.slug = '2'
        a2.content = '2222222'
        a2.status = Article.HIDDEN
        a2.created = datetime(year=1970, month=1, day=2)
        a2.save()
        # make article 3
        a3 = Article()
        a3.title = '3'
        a3.slug = '3'
        a3.content = '3333333'
        a3.status = Article.VISIBLE
        a3.created = datetime(year=2012, month=5, day=20)
        a3.save()
        # test the return 
        n = Article.objects.nav_local()
        # our dict has one item 
        self.assertEqual(1, len(n.items()))
        # and the key is 2012_05
        self.assertEqual(n.keys()[0], '2012_05')
        # and the value is [datetime(2012,5,20,0,0,0), 2]
        self.assertEqual(n['2012_05'], [datetime(2012,5,20,0,0,0), 2])
        # make a2 visible
        a2.status = Article.VISIBLE
        a2.save()
        # now it returns two items
        n = Article.objects.nav_local()
        # our dict has one item 
        self.assertEqual(2, len(n.items()))
        # the keys are in order
        self.assertEqual(n.keys()[0], '2012_05')
        self.assertEqual(n.keys()[1], '1970_01')
        # and the items are correct
        self.assertEqual(n['2012_05'], [datetime(2012,5,20,0,0,0), 2])
        self.assertEqual(n['1970_01'], [datetime(1970,1,2,0,0,0), 1])

    def test_for_month(self):
        """ test that the for month returns only articles that are
        visible and for that month"""
        # make article 1
        a1 = Article()
        a1.title = '1'
        a1.slug = '1'
        a1.content = '1111111'
        a1.status = Article.VISIBLE
        a1.created = datetime(year=2012, month=5, day=20)
        a1.save()
        # make article 2
        a2 = Article()
        a2.title = '2'
        a2.slug = '2'
        a2.content = '2222222'
        a2.status = Article.HIDDEN
        a2.created = datetime(year=2012, month=4, day=20)
        a2.save()
        # make article 3
        a3 = Article()
        a3.title = '3'
        a3.slug = '3'
        a3.content = '3333333'
        a3.status = Article.VISIBLE
        a3.created = datetime(year=2012, month=5, day=20)
        a3.save()
        # 5, 2012 returns 2
        self.assertEqual(2, Article.objects.for_month(
                                month=5,
                                year=2012).count())
        # 4, 2012 returns 0
        self.assertEqual(0, Article.objects.for_month(
                                month=4,
                                year=2012).count())
        # make a2 visible
        a2.status = Article.VISIBLE
        a2.save()
        # 4, 2012 now returns 1
        self.assertEqual(1, Article.objects.for_month(
                                month=4,
                                year=2012).count())

    def test_visible(self):
        """only visible news articles are returned"""
        # make article 1
        a1 = Article()
        a1.title = '1'
        a1.slug = '1'
        a1.content = '1111111'
        a1.status = Article.VISIBLE
        a1.save()
        # make article 2
        a2 = Article()
        a2.title = '2'
        a2.slug = '2'
        a2.content = '2222222'
        a2.status = Article.HIDDEN
        a2.save()
        # make article 3
        a3 = Article()
        a3.title = '3'
        a3.slug = '3'
        a3.content = '3333333'
        a3.status = Article.VISIBLE
        a3.save()
        # visible only returns two
        self.assertEqual(2, Article.objects.visible().count())
        # make a2 visible and now we have three
        a2.status = Article.VISIBLE
        a2.save()
        # visible only returns three
        self.assertEqual(3, Article.objects.visible().count())
