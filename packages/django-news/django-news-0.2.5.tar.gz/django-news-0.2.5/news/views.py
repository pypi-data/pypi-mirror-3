from django.conf import settings
from django.http import HttpResponse, Http404
from django.shortcuts import get_object_or_404
from django.views.generic.list_detail import object_list

from news.constants import NEWS_KEY, NEWS_ARTICLE_PAGINATION
from news.exceptions import NewsException
from news.models import Category, Article, Feed


def run_download(request, *args, **kwargs):
    if request.GET.get('key') == NEWS_KEY:
        articles = 0
        for feed in Feed.objects.filter(active=True):
            try:
                result = feed.process_feed()
            except NewsException:
                pass
            else:
                articles += feed.new_articles_added
        Article.objects.expire_articles()
        return HttpResponse('Done: %d' % (articles))
    return HttpResponse('')


def article_list(request, url_path='', template_name='news/article_list.html'):
    extra_context = {'categories': Category.objects.all()}
    
    if url_path != '':
        category = get_object_or_404(Category, url_path=url_path)
        qs = category.articles.filter(expired=False)
        extra_context.update({'category': category})
    else:
        qs = Article.objects.filter(expired=False)
    
    if request.GET.get('q', None):
        qs = qs.filter(headline__icontains=request.GET['q'])
        extra_context.update({'search_query': request.GET['q']})

    try:
        page = int(request.GET.get('page', 0))
    except ValueError:
        raise Http404
        
    return object_list(
        request,
        queryset=qs,
        template_object_name='article',
        extra_context=extra_context,
        paginate_by=NEWS_ARTICLE_PAGINATION,
        page=page
    )
