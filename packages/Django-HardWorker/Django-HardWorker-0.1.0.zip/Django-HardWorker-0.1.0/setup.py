#/usr/bin/env python

import os
from setuptools import setup, find_packages

def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

setup(
    name = "Django-HardWorker",
    version = "0.1.0",
    author = "Thomas Weholt",
    author_email = "thomas@weholt.org",
    description = ("Simplified background worker for django."),
    license = "Modified BSD",
    keywords = "django background worker",
    url = "https://bitbucket.org/weholt/django-hardworker",
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