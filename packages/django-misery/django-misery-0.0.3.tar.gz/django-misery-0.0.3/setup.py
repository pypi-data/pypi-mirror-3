#!/usr/bin/env python
from setuptools import setup
import os

def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

setup(
    name = "django-misery",
    version = "0.0.3",
    author = "Fabien Schwebel",
    author_email = "fabien@schwebel.com",
    description = ("A simple ban system for Django, that does nasty stuff to trolls wandering on your website."),
    license = "MIT License",
    keywords = "django misery hellban slowban",
    url = "https://bitbucket.org/fschwebel/django-misery/",
    packages=['django_misery'],
    include_package_data=True,
    long_description=read('README.md'),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Environment :: Web Environment",
        "Framework :: Django",
        "Topic :: Utilities",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
)
