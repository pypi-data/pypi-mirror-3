#!/usr/bin/env python

from setuptools import setup, find_packages

setup(
	name = 'django-facebook-comments',
	version = '0.1.2',
	packages = find_packages(),
	include_package_data = True,
	package_data={
		'facebook_comments': ['templates/facebook_comments/*.html',],
	},
	author = 'Shu Zong Chen',
	author_email = 'shu.chen@freelancedreams.com',
	description = 'Drop-in facebook comments for django',
	long_description = \
"""
Pluggable django app for embedding facebook comments on your site.
""",
	license = "MIT License",
	keywords = "django facebook comments templatetag",
	classifiers = [
		'Development Status :: 5 - Production/Stable',
		'Environment :: Web Environment',
		'Framework :: Django',
		'Intended Audience :: Developers',
		'License :: OSI Approved :: MIT License',
		'Operating System :: OS Independent',
		'Programming Language :: Python',
		'Topic :: Software Development :: Libraries :: Application Frameworks',
		'Topic :: Software Development :: Libraries :: Python Modules',
	],
	platforms = ['any'],
	url = 'https://bitbucket.org/sirpengi/django-facebook-comments',
	download_url = 'https://bitbucket.org/sirpengi/django-facebook-comments/downloads',
)

