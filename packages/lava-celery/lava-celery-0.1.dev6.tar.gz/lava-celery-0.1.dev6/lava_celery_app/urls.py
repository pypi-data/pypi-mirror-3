from django.conf.urls.defaults import *


urlpatterns = patterns(
    'lava_celery_app.views',
    url(r'^$', 'index'),
)
