# -*- coding: utf-8 -*-
from distutils.core import setup
from setuptools import find_packages
import os

# taken from django-registration
# Compile the list of packages available, because distutils doesn't have
# an easy way to do this.
packages, data_files = [], []
root_dir = os.path.dirname(__file__)
if root_dir:
    os.chdir(root_dir)

for dirpath, dirnames, filenames in os.walk('prismriver'):
    # Ignore dirnames that start with '.'
    for i, dirname in enumerate(dirnames):
        if dirname.startswith('.'): del dirnames[i]
    if '__init__.py' in filenames:
        pkg = dirpath.replace(os.path.sep, '.')
        if os.path.altsep:
            pkg = pkg.replace(os.path.altsep, '.')
        packages.append(pkg)
    elif filenames:
        prefix = dirpath[11:] # Strip "prismriver/" or "prismriver\"
        for f in filenames:
            data_files.append(os.path.join(prefix, f))

setup(
    name='django-prismriver',
    version='0.12',
    description='A light but cool Django admin theme',
    author=u'Pol Cámara',
    author_email='polcamara@soft10.es',
    url='https://bitbucket.org/PolCPP/django-prismriver',
    package_dir={'prismriver': 'prismriver'},
    packages=packages,
    package_data={'prismriver': data_files},
    license='BSD licence, see LICENCE.txt',
    keywords = "django admin",    
    long_description=open('README.MD').read(),
    zip_safe=False,
)
