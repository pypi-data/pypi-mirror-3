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


def deletemoviedata(imdb_id, imdb_title, alias, outpath, databasepath):
	database = common.init_database(databasepath)
	imdb_title = common.cleanbeforewrite(imdb_title)
	alias = common.cleanbeforewrite(alias)
	textfile = os.path.join(outpath, imdb_title + ' info.txt')
	jsonfile = os.path.join(outpath, 'metadata', alias + '.json')
	similarfolder = os.path.join(outpath, 'metadata', 'Similar to ' + imdb_title)

	if os.path.isfile(textfile):
		os.remove(textfile)
		logging.info('Text file removed.')
	else:
		logging.info('Text file not present.')
	if os.path.isfile(jsonfile):
		os.remove(jsonfile)
		logging.info('Json file removed.')
	else:
		logging.info('Json file not present.')
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


def replace(moviefile, imdburl, posters, trailer, databasepath = common.databasepath):
	
	database = common.init_database()
	movie = common.cleanfilename(os.path.basename(moviefile))
	outpath = os.path.dirname(moviefile)

	idexp = re.compile('tt[0-9]+')
	imdb_id = int(idexp.search(imdburl).group()[2:])
				
	record = ()
	dbdata = {}
	with lite.connect(database) as con:
		cur = con.cursor()

		request = "select moviestext.title, moviestext.id, moviesmisc.alias from \
moviestext, moviesmisc where moviesmisc.alias=\"" + movie +"\" and \
moviesmisc.id=moviestext.id"
		try:
			response = cur.execute(request)
		except lite.Error as e:
			logging.error('Database error: %s', e.args[0])
		else:
			record = response.fetchone()	
			dbdata['imdb_title'] = record[0]
			dbdata['imdb_id'] = record[1]
			dbdata['alias'] = record[2]
	
	if not dbdata['imdb_id'] == imdb_id:
		logging.info('Mismatch found. Deleting old data.')
		deletemoviedata(dbdata['imdb_id'], dbdata['imdb_title'], dbdata['alias'], outpath, databasepath)

		(imdb_apidata, rt_apidata) = getmoviedata.getdatabyid(imdb_id)
		fulldata = getmoviedata.processdata(imdb_apidata, rt_apidata, posters, outpath)
		getmoviedata.storedata(fulldata, movie, outpath)
		
		if trailer == True:
			trailer.trailer(fulldata['imdb_title'], outpath, fulldata['rt_url'])


def main(args):
	"""
	Given a movie file and the URL of the movie's IMDB page, the local data will
	be replaced if inaccurate.

	For help execute: 
	correcter.py --help
	"""
	parser = argparse.ArgumentParser(description='Given a movie file and the \
URL of the movie\'s IMDB page, the local data will be replaced if inaccurate.',
version=common.version)
	parser.add_argument('-a', '--auto', action='store_true', default=False, 
help='Suggest movies with possibly wrong info.')
	parser.add_argument('-m', '--moviefile', action='store', type=str, default='', 
help='The entire path of the movie file.')
	parser.add_argument('-u', '--imdburl', action='store', type=str, default='', 
help='The URL of the movie\'s IMDB page.')
	parser.add_argument('-p', '--posters', action='store_true', default=False, 
help='Download the posters of the movie.')
	parser.add_argument('-t', '--trailer', action='store_true', default=False, 
help='Download the trailer of the movie.')

	common.init_logger(common.loggerpath)
	arguments = parser.parse_args(args)
	if arguments.auto == True:
		auto(arguments.posters, arguments.trailer)
	
	if not arguments.moviefile == '' and not arguments.imdburl == '':
		if not os.path.isfile(arguments.moviefile):
			exit('Moviefile argument is not a valid file.')
		replace(arguments.moviefile, arguments.imdburl, arguments.posters, arguments.trailer)



if __name__ == "__main__":
	sys.exit(main(sys.argv[1:]))
