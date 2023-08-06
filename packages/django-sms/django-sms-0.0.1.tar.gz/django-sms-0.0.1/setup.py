#!/usr/bin/env python
# -*- coding: utf-8 -*-
try:
    from setuptools import setup, find_packages
except ImportError:
    from ez_setup import use_setuptools
    use_setuptools()
    from setuptools import setup, find_packages

setup(
    name='django-sms',
    version='0.0.1',
    description='A Django app for sending SMS with interchangable backends.',
    author='Niels Sandholt Busch',
    author_email='niels.busch@gmail.com',
    url='https://bitbucket.org/resmio/django-sms/',
    long_description=open('README.rst', 'r').read(),
    packages=find_packages(),
    install_requires=['django>=1.3',],
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