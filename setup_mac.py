from setuptools import setup

APP = ['fsin_parser.py']
DATA_FILES = [('', ['js']), ('', ['static']), ('', ['pages.db']), ('', ['1.json'])]
OPTIONS = {'iconfile': 'laptop2.icns',}

setup(
	app = APP,
	data_files = DATA_FILES,
	options = {'py2app': OPTIONS},
	setup_requires = ['py2app'],
)
