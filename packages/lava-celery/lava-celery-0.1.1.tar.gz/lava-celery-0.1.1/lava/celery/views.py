from django.shortcuts import render_to_response
from django.template import RequestContext
from django.conf import settings

from djcelery.models import WorkerState, TaskState
from lava_server.views import index as lava_index
from lava_server.bread_crumbs import (
    BreadCrumb,
    BreadCrumbTrail,
)


@BreadCrumb("Celery", parent=lava_index)
def index(request):
    return render_to_response(
        "lava/celery/index.html", {
            'BROKER_HOST': settings.BROKER_HOST,
            'BROKER_PORT': settings.BROKER_PORT,
            'BROKER_USER': settings.BROKER_USER,
            'BROKER_VHOST': settings.BROKER_VHOST,
            'CELERYD_CONCURRENCY': settings.CELERYD_CONCURRENCY,
            'CELERYD_PREFETCH_MULTIPLIER': settings.CELERYD_PREFETCH_MULTIPLIER,
            'CELERY_RESULT_BACKEND': settings.CELERY_RESULT_BACKEND,
            'CELERY_RESULT_PERSISTENT': settings.CELERY_RESULT_PERSISTENT,
            'worker_state_list': WorkerState.objects.all(),
            'task_state_list': TaskState.objects.all().filter(state__in=('STARTED', 'PENDING', 'RETRY')),
            'bread_crumb_trail': BreadCrumbTrail.leading_to(index)
        }, RequestContext(request))
