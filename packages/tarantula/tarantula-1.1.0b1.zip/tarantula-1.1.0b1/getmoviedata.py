#!/usr/bin/env python3
#-*-coding: utf-8-*-
"""
Copyright 2011 Krishna Sundarram.
This program is distributed under the terms of the MIT License. 

This module calls the imdbapi and rtapi modules.
It retrieves the data and stores it in a dict fulldata.

It subsequently calls the following methods of the module writer:
	writer.totext()
	writer.tojson()
	writer.todatabase()
The module trailer is called for retrieving the trailer of the movie.
Both of the above are used only in main, ie, if the module is used standalone.

"""

import os
import sys
import logging
import argparse
import sqlite3 as lite
import re
import pprint  # present for testing purposes

import rtapi
import imdbapi
import writer
import trailer
import common
 

def test(toprint):
	pp = pprint.PrettyPrinter(indent=4)
	pp.pprint(toprint)


def getdatabyid(imdb_id):
	"""
	Returns a tuple containing the movie data retrieved from the API's.

	Keyword arguments:
	imdb_id			-- The IMDB id of the movie.

	Procedure:
	Query the IMDB API.
	Use the name from that to query the RT API.
	Return the data.

	"""
	logging.info('Querying the IMDb API for ID: %d', imdb_id)
	imdb_apiurl = common.imdb_apiurl
	imdb_apidata = imdbapi.query_api(imdb_apiurl, imdb_id=imdb_id)
	Im = imdbapi.IMDB(imdb_apidata)

	logging.info('Querying the RottenTomatoes API for %s', Im.movietitle())
	rt_apiurl = common.rt_apiurl
	rt_apidata = rtapi.query_api(rt_apiurl, Im.movietitle())
	
	return (imdb_apidata, rt_apidata)


def getdatabyname(moviename):
	"""
	Returns a tuple containing the movie data retrieved from the API's.

	Keyword arguments:
	moviename		-- The name of the movie.

	Procedure:
	Query the IMDB API.
	Query the RT API.
	Return the data.

	"""
	logging.info('Querying the IMDb API for %s', moviename)
	imdb_apiurl = common.imdb_apiurl
	imdb_apidata = imdbapi.query_api(imdb_apiurl, moviename=moviename)

	logging.info('Querying the RottenTomatoes API for %s', moviename)
	rt_apiurl = common.rt_apiurl
	rt_apidata = rtapi.query_api(rt_apiurl, moviename)
	
	return (imdb_apidata, rt_apidata)


def processdata(imdb_apidata, rt_apidata, getposter, moviepath, interactive = False):
	"""
	Processes the data received from the API calls and returns a dict.

	Keyword arguments:
	imdb_apidata	-- Data retrieved from the IMDB API
	rt_apidata		-- Data retrieved from the RT API
	getposter		-- If True, posters are retrieved using this function.
	moviepath		-- The path of the movie file.
	interactive		-- User queried in case of conflict in the two sets of apidata.

	Procedure:
	If rt_apidata is not None, make a list of all ID's returned.
	If imdbid is in that list, add similar data and return all the data(fulldata).
	If imdbid is not in that list, return the IMDB data alone(partialdata).
	"""
	if not os.path.isdir(moviepath):
		outpath = os.path.dirname(moviepath)
	else:
		outpath = moviepath

	Im = imdbapi.IMDB(imdb_apidata)

	rt_ids = []
	rt_alternate = []
	if rt_apidata is not None:
		for movie in rt_apidata['movies']:
			Rt = rtapi.RottenTomatoes(movie)
			if isinstance(Rt.imdbid(), int):
				rt_ids.append(Rt.imdbid())
			if isinstance(Rt.imdbid(), int) and isinstance(Rt.year(), int):
				rt_alternate.append((Rt.year(), Rt.movietitle(), Rt.imdbid()))
	
	if Im.imdbid() in rt_ids and isinstance(Im.imdbid(), int):
		logging.info('ID match: %d', Im.imdbid())
		selectedmovie = rt_ids.index(Im.imdbid())
		Rt = rtapi.RottenTomatoes(rt_apidata['movies'][selectedmovie])
		if getposter == True:
			Rt.get_poster(outpath, 'original')
			Im.get_poster(outpath)
			movietitle = common.cleanbeforewrite(Im.movietitle())
			outpath = os.path.join(outpath, 'metadata', 'Similar to ' + movietitle)
			if not os.path.exists(outpath):
				os.makedirs(outpath)

		logging.info('Querying the RottenTomatoes API for data on similar movies.')
		similarurl = Rt.similar_url()
		similardata = rtapi.query_api(similarurl, '?')
		similartitles = []
		similarposters = []
		try:
			for movie in similardata['movies']:
				Sim = rtapi.RottenTomatoes(movie)
				similartitles.append((Sim.movietitle(), Sim.imdbid()))
				similarposters.append(Sim.posterurls())
				if getposter == True:
					Sim.get_poster(outpath, 'original')
			Rt.similartitles = similartitles
			Rt.similarposters = similarposters
		except TypeError as e:
			logging.error('Did not retrieve data on similar movies.')
		else:
			logging.info('Retrieved similar data successfully.')

		rtdata = Rt.alldata()
		imdbdata = Im.alldata()
		fulldata = dict(rtdata, **imdbdata)
		fulldata['rt_alternate'] = rt_alternate
		logging.info('Data about %s retrieved successfully.', Im.movietitle())
		return fulldata

	if  Im.imdbid() not in rt_ids and isinstance(Im.imdbid(), int):
		logging.error('IDs did not match. IMDB ID: %d', Im.imdbid())

		if interactive == True:
			choice = imode(moviepath, Im.movietitle(), Im.year(), Im.imdbid(), rt_alternate)
			if choice[0] == True:
				imdbid = rt_alternate[choice[1]-1][2]
				imdb_apidata = imdbapi.query_api(common.imdb_apiurl, imdb_id = imdbid)
				return processdata(imdb_apidata, rt_apidata, getposter, moviepath, False)
			else:
				binarychoice = input('Enter URL manually? (y/n):')
				if binarychoice == 'y' or binarychoice == 'Y':
					imdburl = input('IMDB URL:')
					idexp = re.compile('tt[0-9]+')
					imdbid = int(idexp.search(imdburl).group()[2:])
					imdb_apidata = imdbapi.query_api(common.imdb_apiurl, imdb_id = imdbid)
					return processdata(imdb_apidata, rt_apidata, getposter, moviepath, False)

		if getposter == True:
			Im.get_poster(outpath)
		Rt = rtapi.RottenTomatoes(None)
		rtdata = Rt.alldata()
		imdbdata = Im.alldata()
		partialdata = dict(rtdata, **imdbdata)
		partialdata['rt_alternate'] = rt_alternate
		logging.info('Data partially retrieved.')
		return partialdata


def imode(moviepath, title, year, imdbid, alternates):
	"""
	Launches an interactive mode where the user is prompted to pick one of the
	alternative movies.

	"""
	logging.info('Entering interactive mode.')
	text = '{:<3} {:<4} {:<50} {}'
	print('\n\nConflict detected. Please resolve.')
	print(os.path.basename(moviepath))
	print('Imdb title:', title)
	print('Year:', year)
	print('URL:', 'http://www.imdb.com/title/tt' + str(imdbid))
	print(text.format('No.', 'Year', 'Title', 'URL'))
	if len(alternates) > 0:
		for alternate in alternates:
			slno = alternates.index(alternate) + 1
			altyear = alternate[0]
			alttitle = alternate[1]
			alturl = 'http://www.imdb.com/title/tt' + str(alternate[2])
			print(text.format(slno, altyear, alttitle, alturl))
		print('0 None of the above')
		try:
			choice = int(input())
		except ValueError:
			print('Not a valid option. Choosing option 0.')
			return (False, -1)
		if choice in range(1, len(alternates)+1):
			logging.info('Movie chosen: %s', alternates[choice-1][1])
			return (True, choice)
		else:
			logging.info('None of the options chosen')
			return (False, -1)
	else:
		return(False, -1)
			

def storedata(fulldata, moviename, moviepath, databasepath):
	"""
	Stores fulldata in a text file, a json file and the database.
	
	Keyword Arguments:
	fulldata	-- The data from the API's, post processing
	moviename	-- The title of the movie.
	moviepath	-- The path of the movie file.
	databasepath	-- The location of the database.

	
	Once the data has been received, the database is checked if a movie with the
	same ID is already present in the folder.
	If not, then the data is written to a textfile, json file and the database.
	Optional - Retrieve trailerurl.

	"""
	if not os.path.isdir(moviepath):
		moviedirectory = os.path.dirname(moviepath)
	else:
		moviedirectory = moviepath

	presentids = ()
	database = common.init_database(databasepath)
	with lite.connect(database) as con:
		cur = con.cursor()
		try:
			ids = cur.execute("select id from moviestext")
		except lite.Error as e:
			logging.warning('Database is empty. %s', e.args[0])
		else:
			presentids = [ID[0] for ID in ids]

	if not fulldata == None:
		if fulldata['imdb_id'] not in presentids or presentids == ():
			metadatafolder = os.path.join(moviedirectory, 'metadata')
			if not os.path.exists(metadatafolder):
				os.makedirs(metadatafolder)
			fulldata['alias'] = moviename
			fulldata['moviepath'] = moviepath
			writer.tojson(fulldata, metadatafolder)
			writer.totext(fulldata, moviedirectory)
			writer.todatabase(fulldata, databasepath)
			logging.info('Data successfully retrieved for %s', moviename)
		else:
			logging.error('%s is already present in the database.', moviename)
	else:
		logging.error('Data not retrieved for %s', moviename)

	
def main(args):
	"""
	Get info for one movie.

	For help execute: 
	getmoviedata.py --help

	For example: 
	getdata.py -t --posters 'The Shawshank Redemption' '/home/dante/Documents'

	"""
	parser = argparse.ArgumentParser(description='Get info for one movie.', 
version=common.version)
	parser.add_argument('movie', action='store', type=str, 
		help='The title of the movie.')
	parser.add_argument('path', action='store', type=str, 
		help='The location where the data must be stored')
	parser.add_argument('-p', '--posters', action='store_true', default=False, 
		help='Download the posters of the movie.')
	parser.add_argument('-t', '--trailer', action='store_true', default=False, 
		help='Download the trailer of the movie.')
	parser.add_argument('-i', '--interactive', action='store_true', default=False, 
		help='Download in interactive mode. User asked in case of conflicting data.')
	arguments = parser.parse_args(args)
	if not os.path.isdir(arguments.path):
		exit('Not a valid path.')

	moviename = common.cleanfilename(arguments.movie)
	outpath = os.path.join(arguments.path, moviename + ' data')
	metadata = os.path.join(outpath, 'metadata')
	if not os.path.exists(metadata):
		os.makedirs(metadata)

	databasepath = arguments.path
	loggerpath = arguments.path
	common.init_logger(loggerpath)

	(imdb_apidata, rt_apidata) = getdatabyname(moviename)
	fulldata = processdata(imdb_apidata, rt_apidata, arguments.posters, arguments.movie, arguments.interactive)
	storedata(fulldata, moviename, outpath, databasepath)
	
	if arguments.trailer == True:
		fulldata['rt_trailerurl'] = trailer.trailer_url(fulldata['rt_url'])
		trailer.download_trailer(fulldata['imdb_title'], outpath, fulldata['rt_trailerurl'])

if __name__ == "__main__":
	sys.exit(main(sys.argv[1:]))
