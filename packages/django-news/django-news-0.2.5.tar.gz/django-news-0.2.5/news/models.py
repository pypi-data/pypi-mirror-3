import datetime
import feedparser
import re
import time

from django.conf import settings
from django.db import models

from news.constants import (NEWS_EXPIRE_ARTICLES_DAYS, NEWS_BLOCKED_HTML,
    NEWS_BLOCKED_REGEX, NEWS_NO_HTML_TITLES)
from news.exceptions import NewsException


class Source(models.Model):
    """
    A source is a general news source, like CNN, who may provide multiple feeds.
    """
    name = models.CharField(max_length=255)
    url = models.URLField()
    description = models.TextField(blank=True)
    logo = models.ImageField(blank=True, upload_to='images/news_logos')
    
    class Meta:
        ordering = ('name',)
    
    def __unicode__(self):
        return u'%s' % self.name


class WhiteListFilter(models.Model):
    name = models.CharField(max_length=50)
    keywords = models.TextField(help_text="Comma separated list of keywords")
    
    class Meta:
        ordering = ('name',)
    
    def __unicode__(self):
        return u'%s' % self.name
    
    def get_keyword_list(self):
        return [kw.strip() for kw in self.keywords.split(',') if kw.strip()]


class Category(models.Model):
    """
    Categories are populated by collections of feeds and/or other categories.
    They can be configured in a heirarchy, like
    
    /news/sports/basketball/
    
    When feeds are processed, each feed checks to see what categories it can go
    into, and additionally, what white-list filters to apply before adding the
    articles to that category.
    """
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True)
    parent = models.ForeignKey('self', null=True, blank=True, default=None,
        related_name='children', verbose_name='Parent')
    
    # allow categories to include articles from other categories
    include_categories = models.ManyToManyField('self', symmetrical=False,
        through='CategoryRelationship', related_name='including_categories')
    
    # cached field, updated on save
    url_path = models.CharField(max_length=255, editable=False, db_index=True)
    level = models.IntegerField(default=0, editable=False)
    
    class Meta:
        verbose_name_plural = 'categories'
        ordering = ('url_path',)

    def __unicode__(self):
        return u'%s' % self.url_path
    
    def save(self, *args, **kwargs):
        if self.parent:
            # denormalize a path to this category and store its depth
            self.level = self.parent.level + 1
            url_path = '%s%s/' % (self.parent.url_path, self.slug)
        else:
            self.level = 0
            url_path = '%s/' % (self.slug)
 
        self.url_path = url_path
        
        super(Category, self).save(*args, **kwargs)
        
        # update all subcategories in case the url_path changed
        if self.children:
            def update_children(children):
                for child in children:
                    child.save()
                    if child.children:
                        update_children(child.children.all())
            update_children(self.children.all())

    @models.permalink
    def get_absolute_url(self):
        return ('news_article_index', None, {'url_path': self.url_path})


class CategoryRelationship(models.Model):
    """
    Allow a category to include articles from other categories, optionally
    filtering the incoming articles with a white-list.  This operation happens
    when a feed is downloaded, and so only applies to articles going forward
    from the time the relationship is established.
    """
    category = models.ForeignKey(Category, related_name='categories')
    included_category = models.ForeignKey(Category, 
        related_name='included_categories')
    white_list = models.ManyToManyField(WhiteListFilter, blank=True)
    

class Feed(models.Model):
    """
    A feed is the actual RSS/Atom feed that will be downloaded.  It has a
    many-to-many relationship to categories through the FeedCategoryRelationship
    model, which allows white-lists to be applied to the feed before articles
    will be added to the category.
    """
    name = models.CharField(max_length=255)
    url = models.URLField()
    categories = models.ManyToManyField(Category, 
        through='FeedCategoryRelationship')
    source = models.ForeignKey(Source)
    last_download = models.DateField(auto_now=True)
    new_articles_added = models.PositiveSmallIntegerField(default=0, 
        editable=False)
    active = models.BooleanField(default=True)
    
    class Meta:
        ordering = ('name',)
    
    def __unicode__(self):
        return u'%s - %s' % (self.source.name, self.name)
    
    def fetch_feed(self):
        data = feedparser.parse(self.url)
        if 'bozo' in data and data.bozo:
            raise NewsException('Error fetching %s' % self.url)
        return data
    
    def _encode(self, s, e):
        return s.encode(e, 'xmlcharrefreplace')
    
    def get_item_guid(self, item):
        return item.get('id', item.link)
        
    def get_item_summary(self, item):
        summary = ''
        if hasattr(item, "summary"):
            summary = item.summary
        elif hasattr(item, "content"):
            summary = item.content[0].value
        elif hasattr(item, "description"):
            summary = item.description
        return summary
    
    def get_item_pubdate(self, item):
        pubdate = None
        attrs = ['updated_parsed', 'published_parsed', 'date_parsed', 
                 'created_parsed']
        
        for attr in attrs:
            if hasattr(item, attr):
                pubdate = getattr(item, attr)
                break
        
        if pubdate:
            try:
                ts = time.mktime(pubdate)
                return datetime.datetime.fromtimestamp(ts)
            except TypeError:
                pass
        
        return datetime.datetime.now()
    
    def convert_item(self, item, instance=None, encoding='utf-8'):
        if instance is None:
            instance = Article()
        
        if NEWS_NO_HTML_TITLES:
            item.title = re.sub('<[^>]*>', '', item.title)
        
        instance.feed = self
        instance.headline = self._encode(item.title, encoding)[:255]
        instance.guid = self._encode(self.get_item_guid(item), encoding)
        instance.url = self._encode(item.link, encoding)
        
        summary = self._encode(self.get_item_summary(item), encoding)
        if NEWS_BLOCKED_HTML:
            summary = re.sub(NEWS_BLOCKED_REGEX, '', summary)
        instance.content = summary
        
        instance.publish = self.get_item_pubdate(item)
        return instance
    
    def article_passes(self, article, whitelist_queryset):
        keywords = []
        
        # build up a list of all the keywords specified by the relationship
        # between this feed and the category
        for white_list in whitelist_queryset:
            keywords.extend(white_list.get_keyword_list())
        
        if keywords:
            regex = re.compile(r'(%s)' % '|'.join(keywords), re.I)
            if not regex.search(article.headline):
                return False
        
        return True
    
    def get_categories_for_article(self, article):
        # what categories will this article get added to?    
        matching_categories = []
        
        def handle_subcategories(category):
            for category_rel in CategoryRelationship.objects.filter(included_category=category):
                whitelist_qs = category_rel.white_list.all()
                if self.article_passes(article, whitelist_qs):
                    matching_categories.append(category_rel.category)
                handle_subcategories(category_rel.category)
        
        # iterate over the categories associated with this feed
        for category in self.categories.all():
            rel = FeedCategoryRelationship.objects.get(feed=self, category=category)
            if self.article_passes(article, rel.white_list.all()):
                matching_categories.append(category)
                handle_subcategories(category)
        
        return matching_categories
    
    def process_feed(self):
        data = self.fetch_feed()
        
        new_articles_added = 0
        
        # iterate over the entries returned by the feed
        for item in data.entries:
            guid = self.get_item_guid(item)
            
            try:
                article = Article.objects.get(guid=guid, feed=self)
            except Article.DoesNotExist:
                article = Article()
            
            article = self.convert_item(item, article, data.encoding)
            
            matching_categories = self.get_categories_for_article(article)
            
            if len(matching_categories) > 0:
                if not article.pk:
                    new_articles_added += 1
                article.save_base()
                
                article.categories = matching_categories
                article.save()
        
        self.new_articles_added = new_articles_added
        self.last_downloaded = datetime.datetime.now()
        self.save()
        
        return self.new_articles_added


class FeedCategoryRelationship(models.Model):
    feed = models.ForeignKey(Feed)
    category = models.ForeignKey(Category)
    white_list = models.ManyToManyField(WhiteListFilter, blank=True)


class ArticleManager(models.Manager):
    def expired_articles(self):
        if NEWS_EXPIRE_ARTICLES_DAYS:
            delta = datetime.timedelta(days=NEWS_EXPIRE_ARTICLES_DAYS)
            expire_date = datetime.datetime.now() - delta
            return self.filter(date_added__lt=expire_date)
        else:
            return self.none()
        
    def expire_articles(self):
        return self.expired_articles().update(expired=True)

class Article(models.Model):
    headline = models.CharField(max_length=255)
    slug = models.SlugField()
    publish = models.DateTimeField(default=datetime.datetime.now)
    url = models.URLField()
    content = models.TextField()
    guid = models.CharField(max_length=255, blank=True, editable=False)
    date_added = models.DateTimeField(auto_now_add=True)
    expired = models.BooleanField(default=False)
    
    feed = models.ForeignKey(Feed, related_name='articles')
    categories = models.ManyToManyField(Category, related_name='articles')
    
    objects = ArticleManager()
    
    class Meta:
        ordering = ('-publish', 'headline')
    
    def __unicode__(self):
        return u'%s' % self.headline
    
    def get_absolute_url(self):
        return self.url
