#!/usr/bin/env python
# -*- coding: utf-8 -*-
try:
    from setuptools import setup
except ImportError:
    from ez_setup import use_setuptools
    use_setuptools()
    from setuptools import setup

setup(
    name='django-tastypie-with-uploads-dummycache-error500',
    version='1.0.0-beta-red1',
    description='Patched version of Django Tastypie -- check README.rst.',
    author='Daniel Lindsley',
    author_email='daniel@toastdriven.com',
    url='http://github.com/toastdriven/django-tastypie/',
    long_description=open('README', 'r').read(),
    packages=[
        'tastypie',
        'tastypie.utils',
        'tastypie.management',
        'tastypie.management.commands',
    ],
    package_data={
        'tastypie': ['templates/tastypie/*'],
    },
    requires=[
        'mimeparse',
        'python_dateutil(>=1.5, < 2.0)',
    ],
    install_requires=[
        'mimeparse',
        'python_dateutil >= 1.5, < 2.0',
    ],
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Web Environment',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Utilities'
    ],
)
