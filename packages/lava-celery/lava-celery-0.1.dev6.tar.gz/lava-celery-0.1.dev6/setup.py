#!/usr/bin/env python

from setuptools import setup, find_packages


setup(
    name='lava-celery',
    version=":versiontools:lava_celery_app:__version__",
    author="Zygmunt Krynicki",
    author_email="zygmunt.krynicki@linaro.org",
    packages=find_packages(),
    license="AGPL",
    description="Celery integration for LAVA Server",
    entry_points="""
        [lava_server.extensions]
        celery=lava_celery_app.extension:CeleryExtension
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
        'Django >= 1.2',
        'django-celery',
        'lava-server >= 0.2.1',
        'south >= 0.7.3',
        'versiontools >= 1.4',
    ],
    setup_requires=[
        'versiontools >= 1.4',
    ],
    zip_safe=False,
    include_package_data=True
)

