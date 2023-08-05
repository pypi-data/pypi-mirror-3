#-*-coding: utf-8-*-
"""
Copyright 2011 Krishna Sundarram.
This program is distributed under the terms of the MIT License. 

This is a namespace that contains commonly used data and functions.
Since other modules reference this data, changes need to be made only once.

"""
import os
import logging
import re
import unicodedata

version = '1.1.0b1'
#replace databasepath to some other address to change the default location
databasepath = 'home'
loggerpath = 'home'
rt_apikey = '&apikey=rrxumznmjxsy5vn9vrxdrt45'
imdb_apiurl = 'http://www.imdbapi.com/?plot=full&t={}&i={}'
rt_apiurl = 'http://api.rottentomatoes.com/api/public/v1.0/movies.json?q='
filetypes = ['.mp4', '.avi', '.mkv', '.wmv', 'divx', 'xvid', 'mpeg']
apiattempts = 3



def cleanfilename(filename):
	"""Returns a string that is closer to the movie name than the file name."""
	#this needs work
	cleanexp_one = re.compile('(divx|xvid|x264|ac3|dvdrip|r5|bdrip|brrip|mp4|avi|mkv|wmv|divx|xvid|mpeg).*', re.IGNORECASE)
	cleanexp_two = re.compile('(\(|\[).*')
	cleanexp_three = re.compile('.(19[0-9][0-9]|20[0-9][0-9]).*')
	addspaces = re.compile('[^ ]\.[^ ]')

	filename = cleanexp_one.sub('', filename)
	filename = cleanexp_two.sub('', filename)
	filename = cleanexp_three.sub('', filename)
	for m in addspaces.finditer(filename):
		print(str(m))
#	filename = addspaces.sub(' ', filename)
	filename = unicodedata.normalize('NFD', filename).encode('ascii', 'ignore').decode('utf-8')
	return filename


def cleanbeforewrite(filename):
	"""Checks for characters forbidden by filesystems and replaces them."""
	forbidden = re.compile('(/|\\\\|\?|\*|:|\||"|<|>)')
	return forbidden.sub('.', filename)


def init_database(outpath=databasepath):
	"""
	Returns the location of the database file.
	
	Keyword arguments:
	outpath		-- The directory where the database is to be stored.
				Default outpath is the Home directory.
	"""
	if outpath == 'home':
		if os.name == 'posix':
			outpath = os.environ['HOME']
		elif os.name == 'nt':
			outpath = os.environ['HOMEPATH']
	outpath = os.path.join(outpath, '.tarantula')
	if not os.path.exists(outpath):
		os.makedirs(outpath)
	databasename = 'tarantula.db'
	database = os.path.join(outpath, databasename)
	
	return database


def init_logger(outpath=loggerpath):
	"""
	Opens a logging file.
	
	Keyword arguments:
	outpath		-- The directory where the logger is to be stored.
				Default outpath is the Home directory.
	"""
	if outpath == 'home':
		if os.name == 'posix':
			outpath = os.environ['HOME']
		elif os.name == 'nt':
			outpath = os.environ['HOMEPATH']
	outpath = os.path.join(outpath, '.tarantula')
	if not os.path.exists(outpath):
		os.makedirs(outpath)
	loggername = 'tarantula.log'
	logger = os.path.join(outpath, loggername)
	logging.basicConfig(
		filename=logger, filemode='w', level=logging.DEBUG,
		format='%(asctime)s - %(levelname)s - %(message)s')


