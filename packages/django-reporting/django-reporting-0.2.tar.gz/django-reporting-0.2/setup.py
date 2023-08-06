#!/usr/bin/env python
# -*- coding: utf-8 -*-
try:
    from setuptools import setup
except ImportError:
    from ez_setup import use_setuptools
    use_setuptools()
    from setuptools import setup

VERSION = '0.2'

if __name__ == '__main__':
    setup(
        name = 'django-reporting',
        version = VERSION,
        description = "Django Reporting is an application that can be integrated with the Django Admin and allows you to create dynamic reports for your models.",
        long_description = open('README.rst', 'r').read(),
        author = 'Rodrigo Herrera, Vitaliy Kucheryaviy, Marc Garcia',
        author_email = 'rhherrera@gmail.com, ppr.vitaly@gmail.com ,garcia.marc@gmail.com',
        url = 'https://github.com/tryolabs/django-reporting',
        keywords = "django reporting report model models",
        license = 'LGPL',
        packages = (
            'reporting',
        ),
        classifiers = (
            'Development Status :: 4 - Beta',
            'Environment :: Web Environment',
            'Framework :: Django',
            'Intended Audience :: Developers',
            'License :: OSI Approved :: GNU Library or Lesser General Public License (LGPL)',
            'Operating System :: OS Independent',
            'Programming Language :: Python',
            'Topic :: Utilities'
        ),
        zip_safe = False,
        install_requires = (
            'Django>=1.2',
        ),
    )
