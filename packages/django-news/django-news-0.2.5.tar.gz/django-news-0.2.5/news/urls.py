from django.conf.urls.defaults import *

urlpatterns = patterns('news.views',
    url(r'^run-download/$',
        view='run_download',
        name='news_run_download'
    ),
    url(r'^(?P<url_path>[/\w-]*)',
        view='article_list',
        name='news_article_index'
    )
)
