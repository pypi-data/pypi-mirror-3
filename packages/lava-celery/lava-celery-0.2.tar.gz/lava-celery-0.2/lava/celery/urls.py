from django.conf.urls.defaults import *


urlpatterns = patterns(
    'lava.celery.views',
    url(r'^$', 'index'),
)
