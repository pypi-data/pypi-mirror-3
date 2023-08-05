# -*- coding: utf-8 -*-
from distutils.core import setup
from setuptools import find_packages

setup(
    name='django-file-repository',
    version='0.2b',
    author=u'Oscar Carballal Prego',
    author_email='oscar.carballal@cidadania.coop',
    packages=find_packages(),
    url='http://github.com/cidadania/django-file-repository',
    license='GPLv3 license, see LICENSE',
    description='Simple file repository with public/private files, tags and categories.',
    long_description=open('README.rst').read(),
    zip_safe=False,
   
)
