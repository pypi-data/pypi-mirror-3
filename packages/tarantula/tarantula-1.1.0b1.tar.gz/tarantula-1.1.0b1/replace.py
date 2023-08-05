#!/usr/bin/env python3
#-*-coding: utf-8-*-
"""
Copyright 2011 Krishna Sundarram.
This program is distributed under the terms of the MIT License. 

If a movie's info is wrong, then the user is given the option of manually
entering the IMDB URL of the movie and replacing all local data with the new
data.

"""

import os
import sys
import re
import logging
import sqlite3 as lite
import argparse
import pprint  # present for testing purposes

import trailer
import getmoviedata
import common


def test(toprint):
	pp = pprint.PrettyPrinter(indent=4)
	pp.pprint(toprint)


def deletemoviedata(moviepath, databasepath):
	"""
	For a movie file located in moviepath, all data is deleted.
	
	Does not matter if the file exists or not.
	Files deleted:
	* .json file
	* .txt file
	* posters
	* database records

	"""
	database = common.init_database(databasepath)
	record = ()
	with lite.connect(database) as con:
		cur = con.cursor()
		request = "select moviestext.title, moviestext.id, moviesmisc.alias from \
moviestext, moviesmisc where moviesmisc.moviepath=\"" + moviepath +"\" and \
moviesmisc.id=moviestext.id"
		try:
			response = cur.execute(request)
		except lite.Error as e:
			logging.error('Database error: %s', e.args[0])
		else:
			record = response.fetchone()	
			imdb_title = record[0]
			imdb_id = record[1]
			alias = record[2]
	
	imdb_title = common.cleanbeforewrite(imdb_title)
	alias = common.cleanbeforewrite(alias)
	outpath = os.path.dirname(moviepath)
	textfile = os.path.join(outpath, imdb_title + ' info.txt')
	jsonfile = os.path.join(outpath, 'metadata', alias + '.json')
	imdbimage = os.path.join(outpath, imdb_title + ' IMDB.jpg')
	rtimage = os.path.join(outpath, imdb_title + ' RT.jpg')
	filestodelete = [textfile, jsonfile, imdbimage, rtimage]
	similarfolder = os.path.join(outpath, 'metadata', 'Similar to ' + imdb_title)
	
	for filetodelete in filestodelete:
		if os.path.isfile(filetodelete):
			os.remove(filetodelete)
			logging.info(os.path.basename(filetodelete) + ' removed.')
		else:
			logging.info(os.path.basename(filetodelete) + ' not present.')

	if os.path.isdir(similarfolder):
		posters = os.listdir(similarfolder)
		for poster in posters:
			os.remove(poster)
		os.rmdir(similarfolder)
		logging.info('Similar posters removed.')
	else:
		logging.info('Similar folder not present.')

	with lite.connect(database) as con:	
		cur = con.cursor()
		cur.execute('PRAGMA foreign_keys = ON')
		request = "delete from moviestext where id = " + str(imdb_id) # not working
		try:
			cur.execute(request)
		except lite.Error as e:
			logging.error('Database error %s', e.args[0])
		else:
			logging.info('Deleted from database.')


def replace(moviefilepath, posters, trailer, databasepath, imdburl):
	"""Replaces the data of a movie with new data, from the imdburl."""
	
	movie = common.cleanfilename(os.path.basename(moviefilepath))
	outpath = os.path.dirname(moviefilepath)

	idexp = re.compile('tt[0-9]+')
	
	imdb_id = int(idexp.search(imdburl).group()[2:])
	
	logging.info('Mismatch found. Deleting old data.')
	deletemoviedata(moviefilepath, databasepath)

	(imdb_apidata, rt_apidata) = getmoviedata.getdatabyid(imdb_id)
	fulldata = getmoviedata.processdata(imdb_apidata, rt_apidata, posters, outpath)
	getmoviedata.storedata(fulldata, movie, outpath, databasepath)
	
	if trailer == True:
		trailer.trailer(fulldata['imdb_title'], outpath, fulldata['rt_url'])


def suggestions(moviepath, databasepath):
	"""
	For a movie, it finds possible alternatives and launches and prompts
	the user to pick one of them.
	If none are picked, then user is prompted for the IMDB URL of the movie.

	"""
	database = common.init_database(databasepath)
	record = ()
	logging.info('Finding alternates in the database.')
	with lite.connect(database) as con:
		cur = con.cursor()
		mainrequest = "select moviestext.title, moviestext.year, moviestext.id from \
moviestext, moviesmisc where moviesmisc.moviepath= \"" + moviepath + "\" and \
moviesmisc.id=moviestext.id"
		alternates_request = "select alternates.alternateyear, alternates.alternatetitle, \
alternates.alternateid from moviesmisc, alternates where moviesmisc.moviepath= \"" + moviepath + "\" and \
moviesmisc.id=alternates.id order by alternates.alternateyear"
		try:
			mainresponse = cur.execute(mainrequest).fetchone()
			alternates = cur.execute(alternates_request).fetchall()
		except lite.Error as e:
			logging.error('Database error: %s', e.args[0])

	if not mainresponse == None and not alternates == None:
		choice = getmoviedata.imode(moviepath, mainresponse[0], mainresponse[1], mainresponse[2], alternates)
		if choice[0] == True:
			imdbid = alternates[choice[1]-1][2]
			return 'http://www.imdb.com/title/tt' + str(imdbid)
		else:
			binarychoice = input('Enter URL manually? (y/n):')
			if binarychoice == 'y' or binarychoice == 'Y':
				imdburl = input('IMDB URL:')
				idexp = re.compile('tt[0-9]+')
				try:
					imdbid = int(idexp.search(imdburl).group()[2:])
				except AttributeError:
					logging.error('Invalid URL.')
					return False
				else:
					return imdburl
			else:
				return False
	else:
		binarychoice = input('Enter URL manually? (y/n):')
		if binarychoice == 'y' or binarychoice == 'Y':
			imdburl = input('IMDB URL:')
			idexp = re.compile('tt[0-9]+')
			try:
				imdbid = int(idexp.search(imdburl).group()[2:])
			except AttributeError:
				logging.error('Invalid URL.')
				return False
			else:
				return imdburl
		else:
			return False


def main(args):
	"""
	Given a movie file and the URL of the movie's IMDB page(optional), the local data will
	be replaced if inaccurate.

	For help execute: 
	correcter.py --help
	"""
	parser = argparse.ArgumentParser(description='Given a movie file and the \
URL of the movie\'s IMDB page, the local data will be replaced if inaccurate.',
version=common.version)
	parser.add_argument('moviefile', action='store', type=str, 
help='The entire path of the movie file.')
	parser.add_argument('-url', '--imdburl', action='store', type=str, default='', 
help='The URL of the movie\'s IMDB page.')
	parser.add_argument('-p', '--posters', action='store_true', default=False, 
help='Download the posters of the movie.')
	parser.add_argument('-t', '--trailer', action='store_true', default=False, 
help='Download the trailer of the movie.')

	common.init_logger(common.loggerpath)
	databasepath = common.databasepath
	arguments = parser.parse_args(args)
	
	
	if not os.path.isfile(arguments.moviefile):
		exit('Moviefile argument is not a valid file.')
	if arguments.imdburl == '':
		imdb_url = suggestions(arguments.moviefile, databasepath)
		if not imdb_url == False:
			replace(arguments.moviefile, arguments.posters, arguments.trailer, databasepath, imdb_url)
	else:
		replace(arguments.moviefile, arguments.posters, arguments.trailer, databasepath, arguments.imdburl)



if __name__ == "__main__":
	sys.exit(main(sys.argv[1:]))
