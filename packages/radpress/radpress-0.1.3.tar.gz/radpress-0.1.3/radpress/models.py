from django.db import models
from radpress.templatetags.radpress_tags import restructuredtext


class Tag(models.Model):
    name = models.CharField(max_length=50)
    slug = models.SlugField(unique=True)

    def __unicode__(self):
        return unicode(self.name)


class EntryManager(models.Manager):

    def all_published(self):
        return self.filter(is_published=True)


class Entry(models.Model):
    """
    Radpress' main model. It includes articles to show in Radpress mainpage.
    The content body is auto filled by content value after it converted to html
    from restructuredtext. And it has `is_published` to avoid viewing in blog
    list page.

    The `created_at` is set datetime information automatically when a 'new'
    blog entry saved, but `updated_at` will be updated in each save method ran.
    """
    title = models.CharField(max_length=500)
    slug = models.SlugField(unique=True)
    content = models.TextField()
    content_body = models.TextField(editable=False)
    is_published = models.BooleanField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = EntryManager()

    class Meta:
        abstract = True
        ordering = ('-created_at', '-updated_at')

    def __unicode__(self):
        return unicode(self.title)

    def save(self, **kwargs):
        self.content_body = restructuredtext(self.content)

        super(Entry, self).save(**kwargs)


class Article(Entry):
    tags = models.ManyToManyField(
        Tag, null=True, blank=True, through='ArticleTag')


class ArticleTag(models.Model):
    tag = models.ForeignKey(Tag)
    article = models.ForeignKey(Article)

    def __unicode__(self):
        return u"%s - %s" % (self.tag.name, self.article)


class Page(Entry):
    pass


class Menu(models.Model):
    order = models.PositiveSmallIntegerField(default=3)
    page = models.ForeignKey(Page, unique=True)

    class Meta:
        unique_together = ('order', 'page')

    def __unicode__(self):
        return u'%s - %s' % (self.order, self.page.title)
