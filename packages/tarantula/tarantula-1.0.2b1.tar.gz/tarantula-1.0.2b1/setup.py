#!/usr/bin/env python3
#-*-coding: utf-8-*-
"""
Copyright 2011 Krishna Sundarram.
This program is distributed under the terms of the MIT License.

"""

from distutils.core import setup
import common
with open('README.txt') as readme:
   long_description = readme.read()

setup(	name='tarantula',
		version=common.version,
		description='Movie Indexer',
		author='Krishna Sundarram',
		author_email='krishna.sundarram@gmail.com',
		url='http://pypi.python.org/pypi/tarantula/',
		download_url='http://pypi.python.org/pypi/tarantula/#downloads',
		py_modules=[	
					'imdbapi',
					'rtapi',
					'trailer',
					'writer',				
					'getmoviedata',
					'common',
					],
		scripts=[
				'tarantula.py',
				'getmoviedata.py',
				'correcter.py',
				],
		long_description=long_description,
		classifiers=[
#        			'Development Status :: 5 - Production/Stable',
					'Development Status :: 4 - Beta',
			        'Environment :: Console',
			        'Intended Audience :: End Users/Desktop',
					'License :: OSI Approved :: MIT License',
			        'Operating System :: Microsoft :: Windows',
			        'Operating System :: POSIX',
			        'Programming Language :: Python :: 3.2',
					'Topic :: Internet :: WWW/HTTP :: Indexing/Search',
			        ],
	 )
# Hack for uninstallation from http://kmandla.wordpress.com/2009/01/08/there-is-no-setuppy-uninstall/
# python setup.py install --record files.txt
# cat files.txt | xargs rm -rf
