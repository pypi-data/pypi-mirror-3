#!/usr/bin/python
# -*- coding: UTF-8 -*-
import os
from setuptools import setup, find_packages


def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()


VERSION='0.2'

setup(
    name="django-iframetoolbox",
    version=VERSION,
    packages=find_packages('src'),
    package_dir={'':'src'},

    # metadata for upload to PyPI
    license="BSD",
    author="Domantas Jackūnas",
    author_email="Domantas.Jackunas@aurumsocial.com",
    description=("Django set of tools to work inside iframe"),
    url="http://www.aurumsocial.com",
    download_url="https://bitbucket.org/JackLeo/django-iframe",
    keywords="iframe django safari fix",
    long_description=read('README.rst'),

    include_package_data = True,
    zip_safe = False,

    classifiers=[
        'Development Status :: 3 - Alpha',
        'Environment :: Web Environment',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Programming Language :: Python',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
)
