"""
lava.celery.config
==================

This module contains hard-coded configuration for Celery
"""

# TODO: Try to load configuration from lava-server
# TODO: Support command line configuration for server-less operation
CELERY_IMPORTS = (
    'lava.celery.tasks',
)

BROKER_URL = "amqp://guest:guest@localhost:5672//"

CELERY_RESULT_BACKEND = 'amqp'
