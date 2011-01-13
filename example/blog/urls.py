from django.conf.urls.defaults import patterns, url
from blog.models import Post

urlpatterns = patterns('django.views.generic',
    url(r'^(?P<year>\d{4})/(?P<month>\w{3})/(?P<day>\d{1,2})/(?P<slug>[-\w]+)/$',
        'date_based.object_detail',
        {'queryset': Post.objects.published(), 'date_field': 'publish'},
        name='blog_detail'
    ),
    url(r'^(?P<year>\d{4})/(?P<month>\w{3})/(?P<day>\d{1,2})/$',
        'date_based.archive_day',
        {'queryset': Post.objects.published(), 'date_field': 'publish'},
        name='blog_archive_day'
    ),
    url(r'^(?P<year>\d{4})/(?P<month>\w{3})/$',
        'date_based.archive_month',
        {'queryset': Post.objects.published(), 'date_field': 'publish'},
        name='blog_archive_month'
    ),
    url(r'^(?P<year>\d{4})/$',
        'date_based.archive_year',
        {'queryset': Post.objects.published(), 'date_field': 'publish'},
        name='blog_archive_year'
    ),
    url(r'^$',
        'list_detail.object_list',
        {'queryset': Post.objects.published()},
        name='blog_index'
    ),
)
