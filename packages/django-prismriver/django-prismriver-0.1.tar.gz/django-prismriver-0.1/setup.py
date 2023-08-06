# -*- coding: utf-8 -*-
from distutils.core import setup
from setuptools import find_packages

setup(
    name='django-prismriver',
    version='0.1',
    author=u'Pol Cámara',
    author_email='polcamara@soft10.es',
    packages=find_packages(),
    url='https://bitbucket.org/PolCPP/django-prismriver',
    license='BSD licence, see LICENCE.txt',
    description='A light but cool Django admin theme',
    long_description=open('README.MD').read(),
    zip_safe=False,
)