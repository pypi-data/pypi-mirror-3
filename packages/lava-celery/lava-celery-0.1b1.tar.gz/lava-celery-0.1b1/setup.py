#!/usr/bin/env python

from setuptools import setup, find_packages


setup(
    name='lava-celery',
    version=":versiontools:lava.celery:",
    author="Zygmunt Krynicki",
    author_email="zygmunt.krynicki@linaro.org",
    namespace_packages=['lava'],
    packages=['lava.celery'],
    license="AGPL",
    description="Celery integration for LAVA Server",
    entry_points="""
    [lava_server.extensions]
    celery=lava.celery.extension:CeleryExtension
    """,
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: GNU Affero General Public License v3",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 2.6",
        "Programming Language :: Python :: 2.7",
    ],
    install_requires=[
        'lava-server >= 0.2.1',
        'versiontools >= 1.8',
        'django-celery',
    ],
    setup_requires=[
        'versiontools >= 1.8',
    ],
    zip_safe=False,
    include_package_data=True
)

