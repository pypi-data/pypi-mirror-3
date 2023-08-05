#!/usr/bin/env python3
#-*-coding: utf-8-*-
"""
Copyright 2011 Krishna Sundarram.
This program is distributed under the terms of the MIT License. 

This module crawls a directory and identifies movies.
getmoviedata is subsequently called to get the data.

Features yet to implement:
improve regex

"""

import os
import sys
import logging
import sqlite3 as lite
import argparse
import json
import pprint  # present for testing purposes

import getmoviedata
import writer
import trailer
import imdbapi
import rtapi
import common
import replace


def test(toprint):
	pp = pprint.PrettyPrinter(indent=4)
	pp.pprint(toprint)


def crawl(basedirectory, posters, trailer, databasepath, interactive):
	"""
	Crawls basedirectory recursively. Identifies movie files and calls data().

	Keyword Arguments:
	basedirectory	-- The directory to be crawled.
	posters			-- Posters are retrieved along with the movie info.
	trailer			-- The trailer is downloaded if not already present.
	databasepath	-- The location of the database.
	interactive		-- User queried in case of conflict in the two sets of apidata.

	Criteria for a file to be a movie:
	It should have an extension present in the list common.filetypes.
	It should be bigger than 360MB(377487360 bytes).

	If the movie info is present in the database, info is not retrieved.
	else if the movie info is present in a json file, it is written to database.
	else the movie info is retrieved using getmoviedata.

	"""
	database = common.init_database(databasepath)
	for root, dirs, files in os.walk(basedirectory):
		for afile in files:
			moviedirectory = root
			filepath = os.path.join(moviedirectory, afile)
			filesize = os.path.getsize(filepath)
			fileextension = afile[-4:]
			if fileextension in common.filetypes and filesize > 360*((1024)**2):
				moviefile = afile
				moviepath = filepath
				movie = common.cleanfilename(moviefile)

				print(movie)
				if checkdatabase(moviepath, databasepath) == False:
					if checkjson(moviepath, databasepath) == False:
						getmovieinfo(moviepath, posters, databasepath, interactive)
				else:
					pass
				if interactive == True:
					startinteractive(moviepath, posters, trailer, databasepath)
				if trailer == True:
					checktrailer(moviepath, databasepath)
				if posters == True:
					checkimdbposter(moviepath, databasepath)
					checkrtposters(moviepath, 'original', databasepath)				
				logging.info('Operations ended for %s\n', movie)


def checkdatabase(moviepath, databasepath):
	"""
	Checks if the movie is present in the database. If not present, returns False.

	Keyword Arguments:
	moviepath		-- The path of the moviefile
	databasepath	-- The location of the database.

	"""
	database = common.init_database(databasepath)
	movie = common.cleanfilename(os.path.basename(moviepath))
	logging.info('Checking if %s is present in the database.', movie)
	presentmovies = ()
	with lite.connect(database) as con:
		cur = con.cursor()
		try:
			aliases = cur.execute("select alias from moviesmisc")
		except lite.Error as e:
			logging.warning('Database is empty. %s', e.args[0])
		else:
			presentmovies = [alias[0] for alias in aliases]
			
	if movie not in presentmovies or presentmovies == ():
		logging.info('%s is not present in the database.', movie)
		return False
	else:
		logging.info('%s is already present in the database.', movie)
		return True


def checkjson(moviepath, databasepath):
	"""
	Checks if the json file is present in the ./metadata folder.
	If file is present, loads info into database and returns True.
	If file is not present, returns False.

	Keyword Arguments:
	moviepath		-- The path of the moviefile
	databasepath	-- The location of the database.

	"""
	moviedirectory = os.path.dirname(moviepath)
	movie = common.cleanfilename(os.path.basename(moviepath))
	jsonfilename = common.cleanbeforewrite(movie)
	jsonfile = os.path.join(moviedirectory, 'metadata', jsonfilename + '.json')
	logging.info('Checking if a %s.json is present', movie)
	if os.path.isfile(jsonfile):
		logging.info('%s.json found. Writing to database.', movie)
		with open(jsonfile) as j:
			fulldata = json.load(j)
			fulldata['alias'] = movie
			fulldata['moviepath'] = moviepath
			writer.todatabase(fulldata, databasepath)
			return True
	else:
		logging.info('%s.json not found.', movie)
		return False

	
def getmovieinfo(moviepath, posters, databasepath, interactive):
	"""
	Calls the APIs and stores data in text, json and sqlite database.
	It does so by calling the corresponding methods of getmoviedata.

	Keyword Arguments:
	moviepath		-- The path of the moviefile
	posters			-- If true, download posters.
	databasepath	-- The location of the database.
	interactive		-- User queried in case of conflict in the two sets of apidata.
	
	"""
	moviedirectory = os.path.dirname(moviepath)
	movie = common.cleanfilename(os.path.basename(moviepath))
	logging.info('Movie not present. Fetching info about %s', movie)

	(imdb_apidata, rt_apidata) = getmoviedata.getdatabyname(movie)
	fulldata = getmoviedata.processdata(imdb_apidata, rt_apidata, posters, moviedirectory, interactive)
	getmoviedata.storedata(fulldata, movie, moviepath, databasepath)


def startinteractive(moviepath, posters, trailer, databasepath):
	"""
	If the RottenTomatoes info is faulty, user is given alternates to choose
	from.
	moviepath		-- The path of the moviefile
	posters			-- If true, download posters.
	databasepath	-- The location of the database.
	trailer			-- If true, download trailer
	"""
	moviedirectory = os.path.dirname(moviepath)
	movie = common.cleanfilename(os.path.basename(moviepath))
	database = common.init_database(databasepath)

	records = ()
	with lite.connect(database) as con:
		cur = con.cursor()
		request = "select moviesmisc.id from moviesmisc, moviestext \
where moviestext.tomatometer = 'Not Available' and \
moviestext.id = moviesmisc.id and moviesmisc.moviepath = \"" + moviepath + "\""
		try:
			response = cur.execute(request)
		except lite.Error as e:
			logging.info('Database error: %s', e.args[0])
		else:
			records = response.fetchall()
			print(records)
	if not records == () and not records == []:
		imdb_url = replace.suggestions(moviepath, databasepath)
		if not imdb_url == False:
			replace.replace(moviepath, posters, trailer, databasepath, imdb_url)


def checktrailer(moviepath, databasepath):
	"""
	If the trailer of the movie is not present among the files, it is downloaded.
	jsonfile and database are subsequently updated.

	Keyword Arguments:
	moviepath		-- The name of the moviefile, after processing.
	databasepath	-- The location of the database.
	
	"""
	moviedirectory = os.path.dirname(moviepath)
	metadatadirectory = os.path.join(moviedirectory, 'metadata')
	movie = common.cleanfilename(os.path.basename(moviepath))
	files = os.listdir(moviedirectory)
	files.extend(os.listdir(metadatadirectory))

	database = common.init_database(databasepath)
	datum = {}
	with lite.connect(database) as con:
		cur = con.cursor()
		try:
			request = "select moviestext.title, moviesmisc.moviepath, \
moviesmisc.trailerurl, moviesmisc.rturl from moviestext, moviesmisc where \
moviesmisc.alias=\"" + movie +"\" and moviesmisc.id=moviestext.id"
			records = cur.execute(request)
		except lite.Error as e:
			logging.error('Database error: %s', e.args[0])
		else:
			record = records.fetchone()
			datum['title'] = record[0]
			datum['outpath'] = os.path.dirname(record[1])
			datum['trailerurl'] = record[2]
			datum['rturl'] = record[3]

	logging.info('Checking if trailer is already present.')
	if datum['title'] + ' trailer.mp4' not in [trailerfile for trailerfile in files]:
		logging.info('Trailer not present. Retrieving.')
		if datum['trailerurl'][:4] == 'http':
			trailer.download_trailer(datum['title'], datum['outpath'], datum['trailerurl'])
		elif datum['rturl'][:4] == 'http':
			downloadurl = trailer.trailer_url(datum['rturl'])
			trailer.download_trailer(datum['title'], datum['outpath'], downloadurl)
		else:
			logging.error('RottenTomatoes URL not available. Trailer not retrieved.')
	else:
		logging.info('Trailer is present.')
	
	logging.info('Updating .json file.')
	jsonfile = cleanbeforewrite(movie) + '.json'
	jsonfilepath = os.path.join(metadatafolder, jsonfile)
	if os.path.exists(jsonfilepath):
		with open(jsonfilepath) as j:
			fulldata = json.load(j)
		fulldata['rt_trailerurl'] = downloadurl
		with open(jsonfilepath, 'w') as f:	
			json.dump(fulldata, f, indent = 4)
			logging.info('.json file updated.')
	logging.info('Updating database.')
	with lite.connect(database) as con:
		cur = con.cursor()
		try:
			request = "update moviesmisc set moviesmisc.trailerurl= " + downloadurl + " where moviesmisc.alias=" + movie
			cur.execute(request)
		except lite.Error as e:
			logging.error('Database error: %s', e.args[0])
		else:
			logging.info('Database updated.')
				




def checkimdbposter(moviepath, databasepath):
	"""
	If the IMDB poster of the movie is not present among the files, it is downloaded.

	Keyword Arguments:
	moviepath	-- The path of the moviefile
	databasepath	-- The location of the database.
	
	"""
	moviedirectory = os.path.dirname(moviepath)
	movie = common.cleanfilename(os.path.basename(moviepath))
	files = os.listdir(moviedirectory)

	database = common.init_database(databasepath)
	datum = {}
	with lite.connect(database) as con:
		cur = con.cursor()
		try:
			request = "select moviestext.title, moviesmisc.moviepath, \
moviesmisc.imdbposterurl from moviestext, moviesmisc where \
moviesmisc.alias=\"" + movie +"\" and moviesmisc.id=moviestext.id"
			records = cur.execute(request)
		except lite.Error as e:
			logging.error('Database errorlol: %s', e.args[0])
		else:
			for record in records:
				datum['Title'] = record[0]
				datum['Outpath'] = os.path.dirname(record[1])
				datum['Poster'] = record[2]

	logging.info('Checking if IMDB poster is already present.')
	if not datum =={}:
		postername = common.cleanbeforewrite(datum['Title']) + ' IMDB.jpg'
		if  postername not in [poster for poster in files]:
			Im = imdbapi.IMDB(datum)
			Im.get_poster(datum['Outpath'])
		else:
			logging.info('IMDB poster is present.')


def checkrtposters(moviepath, quality, databasepath):
	"""
	If the RT posters of the movie are not present among the files, they are downloaded.

	Keyword Arguments:
	moviepath	-- The path of the moviefile
	quality		-- The quality of the image requested.
	databasepath	-- The location of the database.
	
	"""
	moviedirectory = os.path.dirname(moviepath)
	movie = common.cleanfilename(os.path.basename(moviepath))
	files = os.listdir(moviedirectory)

	database = common.init_database(databasepath)
	moviedata = {}
	similardata =  []
	with lite.connect(database) as con:
		cur = con.cursor()
		try:
			request = "select moviesmisc.rttitle, moviesmisc.moviepath, \
posters.original, posters.detailed, posters.thumbnail, posters.profile from \
moviesmisc, posters where moviesmisc.alias=\"" + movie +"\" and moviesmisc.id = posters.id"
			records = cur.execute(request)
		except lite.Error as e:
			logging.error('Database error: %s', e.args[0])
		else:
			for record in records:
				moviedata['title'] = record[0]
				moviedata['outpath'] = os.path.dirname(record[1])
				moviedata['posters'] = {}
				moviedata['posters']['original'] = record[2]
				moviedata['posters']['detailed'] = record[3]
				moviedata['posters']['thumbnail'] = record[4]
				moviedata['posters']['profile'] = record[5]
		try:
			similarrequest = "select distinct posters.title, moviesmisc.moviepath, \
posters.original, posters.detailed, posters.thumbnail, posters.profile, \
moviestext.title from moviesmisc, posters, similar, moviestext where \
moviesmisc.alias=\"" + movie +"\" and moviesmisc.id = similar.id and \
similar.similarid = posters.id and moviesmisc.id = moviestext.id"
			response = cur.execute(similarrequest)
			similarrecords = response.fetchall()
		except lite.Error as e:
			logging.error('Database error: %s', e.args[0])
		else:
			datum = {}
			for record in similarrecords:
				datum['title'] = record[0]
				datum['outpath'] = os.path.join(os.path.dirname(record[1]), 'metadata', 'Similar to ' + common.cleanbeforewrite(record[6]))
				datum['posters'] = {}
				datum['posters']['original'] = record[2]
				datum['posters']['detailed'] = record[3]
				datum['posters']['thumbnail'] = record[4]
				datum['posters']['profile'] = record[5]
				similardata.append(datum)
				datum = {}

	logging.info('Checking if RT poster is already present.')
	if not moviedata == {}:
		postername = common.cleanbeforewrite(moviedata['title']) + ' RT.jpg'
		if  postername not in [poster for poster in files]:
			logging.info('RT poster not present.')				
			Rt = rtapi.RottenTomatoes(moviedata)
			Rt.get_poster(moviedata['outpath'], quality)
			logging.info('Retrieving similar posters.')
			for similardatum in similardata:
				if not os.path.exists(similardatum['outpath']):
					os.makedirs(similardatum['outpath'])
				Rt = rtapi.RottenTomatoes(similardatum)
				Rt.get_poster(similardatum['outpath'], quality)			
		else:
			logging.info('RT poster is present.')
	else:
		logging.info('RT data not present.')


def deleteorphans(databasepath):
	"""Delete any orphans(entries without movies) found in the DB."""
	database = common.init_database(databasepath)
	logging.info('Checking the database for orphans.')
	moviepaths = ()
	with lite.connect(database) as con:
		cur = con.cursor()
		request = "select moviesmisc.moviepath from moviesmisc"
		try:
			response = cur.execute(request)
		except lite.Error as e:
			logging.error('Database error: %s', e.args[0])
		else:
			moviepaths = response.fetchall()
	for moviepath in moviepaths:
		if os.path.isfile(moviepath[0]):
			fileextension = moviepath[0][-4:]
			filesize = os.path.getsize(moviepath[0])
			if fileextension in common.filetypes and filesize > 360*((1024)**2) :
				logging.info('%s present in the database.', os.path.basename(moviepath[0]))
			else:
				logging.warning('%s present in not the database. Deleting related info.', os.path.basename(moviepath[0]))
				replace.deletemoviedata(moviepath[0], databasepath)
		else:
			logging.warning('%s present in not the database. Deleting related info.', os.path.basename(moviepath[0]))
			replace.deletemoviedata(moviepath[0], databasepath)


def main(args):
	"""
	Gets info, posters, and trailers for all the movies in the directory. Also
	creates a local database for easy access.

	For help execute: 
	tarantula.py --help

	The data is stored in .txt and .json files in the movie folder.
	It is also entered into a database stored in the user's home directory.

	Any actions performed by the program are recorded in the logger file
	.tarantula.log stored in the user's home directory.
	
	"""
	parser = argparse.ArgumentParser(description='Gets info, posters, and \
trailers for all the movies in the directory. Also creates a local database \
for easy access.', version=common.version)
	parser.add_argument('directory', action='store', type=str, 
		help='The directory to crawl.')
	parser.add_argument('-p', '--posters', action='store_true', default=False, 
		help='Download the posters of the movies.')
	parser.add_argument('-t', '--trailer', action='store_true', default=False, 
		help='Download the trailer of the movies.')
	parser.add_argument('-i', '--interactive', action='store_true', default=False, 
		help='Download in interactive mode. User asked in case of conflicting data.')
	parser.add_argument('-o', '--orphans', action='store_true', default=False, 
		help='Delete any orphans(entries without movies) found in the DB.')

	arguments = parser.parse_args(args)
	if not os.path.isdir(arguments.directory):
		exit('Not a valid path.')
	#For a custom database location, replace the following line.
	databasepath = common.databasepath
	common.init_logger()

	if arguments.orphans == True:
		deleteorphans(common.databasepath)
	logging.info('tarantula starting to crawl.\n')
	crawl(arguments.directory, arguments.posters, arguments.trailer, common.databasepath, arguments.interactive)


if __name__ == "__main__":
	sys.exit(main(sys.argv[1:]))
