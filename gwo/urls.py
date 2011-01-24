from django.conf.urls.defaults import *
from gwo.models import GwoExperiment


urlpatterns = patterns('',
    url(
        r'^(?P<object_id>\d+)/goal/$', 
        'django.views.generic.list_detail.object_detail', 
        {'queryset': GwoExperiment.objects.all()},
        name='goal'),
)
