import os

from lava_server.extension import LavaServerExtension


class CeleryExtension(LavaServerExtension):

    @property
    def app_name(self):
        return "lava.celery"

    @property
    def name(self):
        return "Celery"

    @property
    def main_view_name(self):
        return "lava.celery.views.index"

    @property
    def description(self):
        return "Celery Integration"

    @property
    def version(self):
        import lava.celery
        import versiontools
        return versiontools.format_version(lava.celery.__version__, lava.celery)

    def contribute_to_settings(self, settings_module):
        super(CeleryExtension, self).contribute_to_settings(settings_module)
        settings_module['INSTALLED_APPS'].extend([
            "djcelery",
        ])
        settings_module.update({
            'BROKER_HOST': '127.0.0.1',
            'BROKER_PORT': 5672,
            'BROKER_USER': 'guest',
            'BROKER_PASSWORD': 'guest',
            'BROKER_VHOST': '/'
        })
        import djcelery
        djcelery.setup_loader()

    def contribute_to_settings_ex(self, settings_module, settings_object):
        settings_module.update({
            # We want to automatically determine the number of workers
            "CELERYD_CONCURRENCY": settings_object.get_setting("CELERYD_CONCURRENCY", None),
            # We want to prefetch at most one task, this is better as lava prefers long running tasks
            "CELERYD_PREFETCH_MULTIPLIER": settings_object.get_setting("CELERYD_PREFETCH_MULTIPLIER", 1),
            # We want to send results back as amqp messages
            "CELERY_RESULT_BACKEND": settings_object.get_setting("CELERY_RESULT_BACKEND", "amqp"),
            # We want persistent tasks by default (survive broker restarts)
            "CELERY_RESULT_PERSISTENT": settings_object.get_setting("CELERY_RESULT_PERSISTENT", True),
            # Broker configuration
            'BROKER_HOST': settings_object.get_setting("BROKER_HOST", '127.0.0.1'),
            'BROKER_PORT': settings_object.get_setting("BROKER_PORT", 5672),
            'BROKER_USER': settings_object.get_setting("BROKER_USER", 'guest'),
            'BROKER_PASSWORD': settings_object.get_setting("BROKER_PASSWORD", 'guest'),
            'BROKER_VHOST': settings_object.get_setting("BROKER_VHOST", '/'),
        })
