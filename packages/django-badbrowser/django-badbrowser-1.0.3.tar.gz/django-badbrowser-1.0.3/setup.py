#!/usr/bin/env python
try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup
import os

from django_badbrowser import __version__

long_description = open(os.path.join(os.path.dirname(__file__), "README.textile")).read()

setup(
	name="django-badbrowser",
	version=__version__,
	url="http://github.com/adamcharnock/django-badbrowser",
	download_url="git@github.com:adamcharnock/django-badbrowser.git",
	description="Browser detection (including browser upgrade notices) for Django",
	long_description=long_description,
	author="Adam Charnock",
	author_email="adam@playnice.ly",
	platforms=["any"],
	license="MIT",
	packages=[
		"django_badbrowser",
	],
	classifiers=[
		"Development Status :: 4 - Beta",
		"License :: OSI Approved :: MIT License",
		"Environment :: Web Environment",
		"Framework :: Django",
		"Intended Audience :: Developers",
		"Operating System :: OS Independent",
		"Programming Language :: Python",
		"Topic :: Software Development :: Libraries :: Application Frameworks",
		"Topic :: Software Development :: Libraries :: Python Modules",
		"Topic :: Internet :: WWW/HTTP :: Browsers",
	],
	install_requires=[
		"httpagentparser",
	],
)
