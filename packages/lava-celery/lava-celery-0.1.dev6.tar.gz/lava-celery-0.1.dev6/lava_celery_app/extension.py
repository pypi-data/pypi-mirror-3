import os

from lava_server.extension import LavaServerExtension


class CeleryExtension(LavaServerExtension):

    @property
    def app_name(self):
        return "lava_celery_app"

    @property
    def name(self):
        return "Celery"

    @property
    def main_view_name(self):
        return "lava_celery_app.views.index"

    @property
    def description(self):
        return "Celery Integration"

    @property
    def version(self):
        from lava_celery_app import __version__
        import versiontools
        return versiontools.format_version(__version__)

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
        pass
