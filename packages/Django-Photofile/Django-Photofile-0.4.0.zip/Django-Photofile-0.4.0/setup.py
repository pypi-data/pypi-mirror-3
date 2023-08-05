#/usr/bin/env python

import os
from setuptools import setup, find_packages

def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

setup(
    name = "Django-Photofile",
    version = "0.4.0",
    author = "Thomas Weholt",
    author_email = "thomas@weholt.org",
    description = ("Templatetags for thumbnail generation, with automatic rotation based on EXIF.Orientation. Among other things."),
    license = "Modified BSD",
    keywords = "photo thumbnail generation django metadata",
    url = "https://bitbucket.org/weholt/django-photofile",
    install_requires = ['django', 'pil',],
    zip_safe = False,
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Framework :: Django',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Database',
        ],
    packages = find_packages(),
    long_description=read('README.txt'),
)