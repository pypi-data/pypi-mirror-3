from setuptools import setup, find_packages

setup (
	name = 'toCSS',
	version = '0.1',
	scripts = ['toCSS.py'],
	author = 'Alexander Guinness',
	author_email = 'monolithed@gmail.com',
	description = 'This module provides a function that converts a {dict} into valid and formatted CSS code presented by a string',
	classifiers = [
		'Programming Language :: Python',
		('Topic :: Software Development :: Libraries :: Python Modules')
	],
	packages = find_packages(),
	license = 'PSF, MIT',
	keywords = 'Convert {dict} to valid and formatted CSS code',
	url = 'https://github.com/monolithed/toCSS',
	download_url = 'https://github.com/monolithed/toCSS/downloads'
)