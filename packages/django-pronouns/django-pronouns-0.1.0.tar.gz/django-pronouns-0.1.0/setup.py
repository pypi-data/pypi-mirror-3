#!/usr/bin/env python

try:
	from setuptools import setup, find_packages
except ImportError:
	from ez_setup import use_setuptools
	use_setuptools()
	from setuptools import setup, find_packages

setup(
    name='django-pronouns',
    version="0.1.0",
    description='Generic pronoun handling for Django applications',
    author='Tim Heap',
    author_email='heap.tim@gmail.com',
    url='https://bitbucket.org/tim_heap/django-pronouns',
    packages=['django_pronouns', 'django_pronouns.fixtures'],
    package_data={'django_pronouns': ['fixtures/*']},
    classifiers=[
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Framework :: Django',
    ],
)

