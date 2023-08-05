
from south.db import db
from django.db import models
from news.models import *

class Migration:
    
    def forwards(self, orm):
        
        # Adding model 'Feed'
        db.create_table('news_feed', (
            ('id', orm['news.Feed:id']),
            ('name', orm['news.Feed:name']),
            ('url', orm['news.Feed:url']),
            ('source', orm['news.Feed:source']),
            ('last_download', orm['news.Feed:last_download']),
            ('new_articles_added', orm['news.Feed:new_articles_added']),
            ('active', orm['news.Feed:active']),
        ))
        db.send_create_signal('news', ['Feed'])
        
        # Adding model 'Category'
        db.create_table('news_category', (
            ('id', orm['news.Category:id']),
            ('name', orm['news.Category:name']),
            ('slug', orm['news.Category:slug']),
            ('parent', orm['news.Category:parent']),
            ('url_path', orm['news.Category:url_path']),
            ('level', orm['news.Category:level']),
        ))
        db.send_create_signal('news', ['Category'])
        
        # Adding model 'CategoryRelationship'
        db.create_table('news_categoryrelationship', (
            ('id', orm['news.CategoryRelationship:id']),
            ('category', orm['news.CategoryRelationship:category']),
            ('included_category', orm['news.CategoryRelationship:included_category']),
        ))
        db.send_create_signal('news', ['CategoryRelationship'])
        
        # Adding model 'Source'
        db.create_table('news_source', (
            ('id', orm['news.Source:id']),
            ('name', orm['news.Source:name']),
            ('url', orm['news.Source:url']),
            ('description', orm['news.Source:description']),
            ('logo', orm['news.Source:logo']),
        ))
        db.send_create_signal('news', ['Source'])
        
        # Adding model 'WhiteListFilter'
        db.create_table('news_whitelistfilter', (
            ('id', orm['news.WhiteListFilter:id']),
            ('name', orm['news.WhiteListFilter:name']),
            ('keywords', orm['news.WhiteListFilter:keywords']),
        ))
        db.send_create_signal('news', ['WhiteListFilter'])
        
        # Adding model 'FeedCategoryRelationship'
        db.create_table('news_feedcategoryrelationship', (
            ('id', orm['news.FeedCategoryRelationship:id']),
            ('feed', orm['news.FeedCategoryRelationship:feed']),
            ('category', orm['news.FeedCategoryRelationship:category']),
        ))
        db.send_create_signal('news', ['FeedCategoryRelationship'])
        
        # Adding model 'Article'
        db.create_table('news_article', (
            ('id', orm['news.Article:id']),
            ('headline', orm['news.Article:headline']),
            ('slug', orm['news.Article:slug']),
            ('publish', orm['news.Article:publish']),
            ('url', orm['news.Article:url']),
            ('content', orm['news.Article:content']),
            ('guid', orm['news.Article:guid']),
            ('date_added', orm['news.Article:date_added']),
            ('expired', orm['news.Article:expired']),
            ('feed', orm['news.Article:feed']),
        ))
        db.send_create_signal('news', ['Article'])
        
        # Adding ManyToManyField 'CategoryRelationship.white_list'
        db.create_table('news_categoryrelationship_white_list', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('categoryrelationship', models.ForeignKey(orm.CategoryRelationship, null=False)),
            ('whitelistfilter', models.ForeignKey(orm.WhiteListFilter, null=False))
        ))
        
        # Adding ManyToManyField 'Article.categories'
        db.create_table('news_article_categories', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('article', models.ForeignKey(orm.Article, null=False)),
            ('category', models.ForeignKey(orm.Category, null=False))
        ))
        
        # Adding ManyToManyField 'FeedCategoryRelationship.white_list'
        db.create_table('news_feedcategoryrelationship_white_list', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('feedcategoryrelationship', models.ForeignKey(orm.FeedCategoryRelationship, null=False)),
            ('whitelistfilter', models.ForeignKey(orm.WhiteListFilter, null=False))
        ))
        
    
    
    def backwards(self, orm):
        
        # Deleting model 'Feed'
        db.delete_table('news_feed')
        
        # Deleting model 'Category'
        db.delete_table('news_category')
        
        # Deleting model 'CategoryRelationship'
        db.delete_table('news_categoryrelationship')
        
        # Deleting model 'Source'
        db.delete_table('news_source')
        
        # Deleting model 'WhiteListFilter'
        db.delete_table('news_whitelistfilter')
        
        # Deleting model 'FeedCategoryRelationship'
        db.delete_table('news_feedcategoryrelationship')
        
        # Deleting model 'Article'
        db.delete_table('news_article')
        
        # Dropping ManyToManyField 'CategoryRelationship.white_list'
        db.delete_table('news_categoryrelationship_white_list')
        
        # Dropping ManyToManyField 'Article.categories'
        db.delete_table('news_article_categories')
        
        # Dropping ManyToManyField 'FeedCategoryRelationship.white_list'
        db.delete_table('news_feedcategoryrelationship_white_list')
        
    
    
    models = {
        'news.article': {
            'categories': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['news.Category']"}),
            'content': ('django.db.models.fields.TextField', [], {}),
            'date_added': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'expired': ('django.db.models.fields.BooleanField', [], {'default': 'False', 'blank': 'True'}),
            'feed': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'articles'", 'to': "orm['news.Feed']"}),
            'guid': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'headline': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'publish': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'slug': ('django.db.models.fields.SlugField', [], {'max_length': '50', 'db_index': 'True'}),
            'url': ('django.db.models.fields.URLField', [], {'max_length': '200'})
        },
        'news.category': {
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'include_categories': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['news.Category']", 'symmetrical': 'False'}),
            'level': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'parent': ('django.db.models.fields.related.ForeignKey', [], {'default': 'None', 'related_name': "'children'", 'null': 'True', 'blank': 'True', 'to': "orm['news.Category']"}),
            'slug': ('django.db.models.fields.SlugField', [], {'unique': 'True', 'max_length': '50', 'db_index': 'True'}),
            'url_path': ('django.db.models.fields.CharField', [], {'max_length': '255', 'db_index': 'True'})
        },
        'news.categoryrelationship': {
            'category': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'categories'", 'to': "orm['news.Category']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'included_category': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'included_categories'", 'to': "orm['news.Category']"}),
            'white_list': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['news.WhiteListFilter']", 'blank': 'True'})
        },
        'news.feed': {
            'active': ('django.db.models.fields.BooleanField', [], {'default': 'True', 'blank': 'True'}),
            'categories': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['news.Category']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'last_download': ('django.db.models.fields.DateField', [], {'auto_now': 'True', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'new_articles_added': ('django.db.models.fields.PositiveSmallIntegerField', [], {'default': '0'}),
            'source': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['news.Source']"}),
            'url': ('django.db.models.fields.URLField', [], {'max_length': '200'})
        },
        'news.feedcategoryrelationship': {
            'category': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['news.Category']"}),
            'feed': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['news.Feed']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'white_list': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['news.WhiteListFilter']", 'blank': 'True'})
        },
        'news.source': {
            'description': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'logo': ('django.db.models.fields.files.ImageField', [], {'max_length': '100', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'url': ('django.db.models.fields.URLField', [], {'max_length': '200'})
        },
        'news.whitelistfilter': {
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'keywords': ('django.db.models.fields.TextField', [], {}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        }
    }
    
    complete_apps = ['news']
