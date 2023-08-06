from setuptools import setup, find_packages

setup (
	name = 'pyprint_r',
	version = '0.1',
	scripts = ['pyprint_r.py'],
	author = 'Alexander Guinness',
	author_email = 'monolithed@gmail.com',
	description = 'This module provides a function that prints human-readable information about the object',
	classifiers = [
		'Programming Language :: Python',
		('Topic :: Software Development :: Libraries :: Python Modules')
	],
	packages = find_packages(),
	license = 'PSF, MIT',
	keywords = 'print_r print human-readable information',
	url = 'https://github.com/monolithed/print_r',
	download_url='https://github.com/monolithed/print_r/downloads'
)