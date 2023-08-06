#/usr/bin/env python

import os
from setuptools import setup, find_packages

def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

setup(
    name = "Django-MobilityHelpers",
    version = "0.1.0a",
    author = "Thomas Weholt",
    author_email = "thomas@weholt.org",
    description = ("Simple middleware and helper function to help handle request from mobile devices."),
    license = "Modified BSD",
    keywords = "django middleware mobile devices",
    url = "https://bitbucket.org/weholt/django-mobilityhelpers",
    install_requires = ['django',],
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