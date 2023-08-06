#!/usr/bin/env python

from distutils.core import setup, Extension

setup(
	name				=	'speedyxml',
	version				=	'0.1',
	description			=	'Speedy XML parser for Python',
	author				=	'kilroy',
	author_email		=	'kilroy@uni-koblenz.de',
	license				=	'LGPL',
	py_modules			=	[],
	ext_modules			=	[
		Extension('speedyxml', ['src/speedyxml.c'])
	],
	classifiers			=	[
		'Development Status :: 4 - Beta',
		'Intended Audience :: Developers',
		'Natural Language :: English',
		'Operating System :: POSIX',
		'Programming Language :: Python',
		'Topic :: Software Development :: Libraries :: Python Modules',
		'Topic :: Text Processing :: Markup :: XML',
		'License :: OSI Approved :: GNU Library or Lesser General Public License (LGPL)',
	],
)
