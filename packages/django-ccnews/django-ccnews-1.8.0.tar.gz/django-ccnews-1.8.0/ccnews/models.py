from django.db import models
from ccthumbs.fields import ImageWithThumbsField
from ccnews import settings as c_settings
from ccnews.managers import ArticleManager
from ccnews import listeners


class Article(models.Model):
    VISIBLE = 1
    HIDDEN = 0
    STATUS_CHOICES = (
            (HIDDEN, 'Hidden'),
            (VISIBLE, 'Visible')
    )
    title = models.CharField(
            max_length=255)
    slug = models.SlugField(
            unique=True)
    content = models.TextField()
    content_rendered = models.TextField(
            blank=True,
            null=True)
    excerpt = models.TextField(
            blank=True,
            null=True)
    status = models.PositiveSmallIntegerField(
            default=c_settings.CCNEWS_DEFAULT_STATUS,
            choices=STATUS_CHOICES)
    created = models.DateTimeField(
            blank=True,
            null=True)
    modified = models.DateTimeField(
            blank=True,
            null=True,
            auto_now=True)

    objects = ArticleManager()

    class Meta:
        ordering = ['-created']

    def __unicode__(self):
        return u'%s' % self.title

    @models.permalink
    def get_absolute_url(self):
        return ('ccnews:view', (),{
            'year': self.created.year,
            'month': self.created.month,
            'slug': self.slug})

    @property
    def description(self):
        return u'%s' % self.content_rendered[:100]

class ArticleImage(models.Model):
    article = models.ForeignKey(Article)
    src = ImageWithThumbsField(
            upload_to='ccnews/%Y/%m/%d',
            sizes=c_settings.CCNEWS_IMAGE_SIZES)
    title = models.CharField(
            max_length=255,
            null=True,
            blank=True)
    order = models.DecimalField(
            default=10.00,
            max_digits=8,
            decimal_places=2)
    created = models.DateTimeField(
            blank=True,
            null=True,
            auto_now_add=True)
    modified = models.DateTimeField(
            blank=True,
            null=True,
            auto_now=True)
    
    class Meta:
        ordering = ['order']

    def __unicode__(self):
        return u'news image: %s' % self.pk


class ArticleAttachment(models.Model):
    article = models.ForeignKey(Article)
    src = models.FileField(
            upload_to='ccnews/%Y/%m/%d')
    title = models.CharField(
            max_length=255,
            null=True,
            blank=True)
    order = models.DecimalField(
            default=10.00,
            max_digits=8,
            decimal_places=2)
    created = models.DateTimeField(
            blank=True,
            null=True,
            auto_now_add=True)
    modified = models.DateTimeField(
            blank=True,
            null=True,
            auto_now=True)
    
    def __unicode__(self):
        return u'article attachment: %s' % self.pk

    class Meta:
        ordering = ['order']

models.signals.pre_save.connect(
        listeners.set_attachment_title,
        sender=ArticleAttachment,
        dispatch_uid='ccnews_set_attachment_title')

models.signals.pre_save.connect(
        listeners.set_excerpt,
        sender=Article,
        dispatch_uid='ccnews_set_excerpt')

models.signals.pre_save.connect(
        listeners.set_content_rendered,
        sender=Article,
        dispatch_uid='ccnews_set_content_rendered')

models.signals.pre_save.connect(
        listeners.set_created,
        sender=Article,
        dispatch_uid='ccnews_set_created')
