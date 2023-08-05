from django.conf.urls.defaults import *

urlpatterns = patterns('',
    url(r'^news/', include('news.urls')),
)
