#-*-coding: utf-8-*-
"""
Copyright 2011 Krishna Sundarram.
This program is distributed under the terms of the MIT License. 

Methods:
	totext()
	todatabase()
	tojson()

Unfortunately, this module does not adhere to PEP-8.
My apologies if you find it difficult to read it.

Imported by getdata.

"""

import json
import os
import sqlite3 as lite
import logging

import common
#import pprint  # present for testing purposes
 

def test(toprint):
	pp = pprint.PrettyPrinter(indent=4)
	pp.pprint(toprint)


def tojson(fulldata, outpath):
	"""
	Writes the data to a json file for easy recovery.

	Keyword Arguments:
	fulldata		-- All the data extracted from RT and IMDB.
	outpath			-- The location of the text file to be written.

	"""
	filename = common.cleanbeforewrite(fulldata['alias']) + '.json'
	outpathfile = os.path.join(outpath, filename)
	try:
		logging.info('Writing %s to %s', filename, outpath)
		with open(outpathfile, 'w') as f:	
			json.dump(fulldata, f, indent = 4)
	except IOError as e:
		logging.error('Could not write to json because the folder %s does not exist.', outpath)
	else:
		logging.info('Written to %s successfully.', filename)


def splitter(field, fulldata):
	"""Returns a list of tuples. Used for separating comma separated data."""
	datalist = []
	data = fulldata[field].split(', ')
	for datum in data:
		datalist.append((fulldata['imdb_id'], datum))	
	return datalist


def todatabase(fulldata, databasepath=common.databasepath):
	"""
	Writes the data to the appropriate tables in test.db.

	Keyword Arguments:
	fulldata		-- All the data extracted from RT and IMDB.
	database		-- The location of the database.

	In table moviestext - id, title, released, year, censorrating, runtimetext, 
						  runtimenumber, plot, imdbrating, votes, tomatometer, 
						  tomatorating, consensus
	In table moviesmisc - id, rttitle, moviepath, alias, trailerurl, rturl, imdburl,
						  imdbposterurl
	In table genres - id, genre
	In table directors - id, director
	In table writers - id, writer
	In table characters - id, character, actor
	In table similar - id, similarid, similartitle
	In table posters - id, title, imdb, original, detailed, thumbnail, profile
	In table alternates - id, alternateyear, alternatetitle, alternateid

	The id field in all tables except moviestext is a foreign key referencing
	the id field of moviestext. Therefore, if a record of id = 203423 (say)
	is deleted, then all records in the database having that id will also
	be deleted.  
	Note that moviepath and alias are not retrieved in getdata. 
	They must be added, manually before this function is called.

	"""
	database = common.init_database(databasepath)
	databasename = os.path.basename(database)
	databasedir = os.path.dirname(database)

	moviestextdata = (
		fulldata['imdb_id'],
		fulldata['imdb_title'],
		fulldata['imdb_released'],
		fulldata['imdb_year'],
		fulldata['imdb_censor_rating'],
		fulldata['imdb_runtime'],
		fulldata['rt_runtime'],
		fulldata['imdb_plot'],
		fulldata['imdb_rating'],
		fulldata['imdb_votes'],
		fulldata['rt_tomatometer'],
		fulldata['rt_tomatorating'],
		fulldata['rt_consensus'],
		)	
	moviesmiscdata = (
		fulldata['imdb_id'],
		fulldata['rt_title'],
		fulldata['moviepath'],
		fulldata['alias'],
		fulldata['rt_trailerurl'],
		fulldata['rt_url'],
		fulldata['imdb_url'],
		fulldata['imdb_posterurl'],
		)
	genredata = splitter('imdb_genres', fulldata)
	directordata = splitter('imdb_directors', fulldata)
	writerdata = splitter('imdb_writers', fulldata)

	if isinstance(fulldata['rt_characters'], list):
		characterdata =[]
		for pair in fulldata['rt_characters']:
			characterdata.append((fulldata['imdb_id'], pair['character'], pair['actor']))
	else:			
		characterdata = splitter('imdb_characters', fulldata)

	similardata = []
	for pair in fulldata['rt_similartitles']:
		try:
			similardata.append((fulldata['imdb_id'], pair[1], pair[0]))
		except (IndexError, TypeError):
			pass

	try:
		posterdata = [(fulldata['imdb_id'],
			fulldata['rt_title'],
			fulldata['rt_posterurl']['original'],
			fulldata['rt_posterurl']['detailed'],
			fulldata['rt_posterurl']['thumbnail'],
			fulldata['rt_posterurl']['profile'])]
		for movie in fulldata['rt_similarposters']:
			index = fulldata['rt_similarposters'].index(movie)		
			posterdata.append((fulldata['rt_similartitles'][index][1],
			fulldata['rt_similartitles'][index][0],
			movie['original'],
			movie['detailed'],
			movie['thumbnail'],
			movie['profile']))
	except (IndexError, TypeError):
		posterdata = []

	alternatedata = []
	for triad in fulldata['rt_alternate']:
		try:
			alternatedata.append((fulldata['imdb_id'], triad[0], triad[1], triad[2]))
		except (IndexError, TypeError):
			pass

	with lite.connect(database) as con:
		cur = con.cursor()
		cur.execute('PRAGMA foreign_keys = ON')
		cur.execute("create table if not exists moviestext(id INT UNIQUE, \
title TEXT, released TEXT, year INT, censorrating TEXT, runtimetext TEXT, \
runtimenumber INT, Plot TEXT, imdbrating INT, votes INT, tomatometer int, \
tomatorating TEXT, consensus TEXT)")
		cur.execute("create table if not exists moviesmisc(id INT, rttitle TEXT, \
moviepath TEXT, alias TEXT, trailerurl TEXT, rturl TEXT, imdburl TEXT, \
imdbposterurl TEXT, foreign key(id) references moviestext(id) on delete cascade)")
		cur.execute("create table if not exists genres(id INT, genre TEXT, foreign key (id) references moviestext (id) on delete cascade)")
		cur.execute("create table if not exists directors(id INT, director TEXT, foreign key (id) references moviestext (id) on delete cascade)")
		cur.execute("create table if not exists writers(id INT, writer TEXT, foreign key (id) references moviestext (id) on delete cascade)")
		cur.execute("create table if not exists characters(id INT, character TEXT, \
actor TEXT, foreign key (id) references moviestext (id) on delete cascade)")
		cur.execute("create table if not exists similar(id INT, similarid INT, \
similartitle TEXT, foreign key (id) references moviestext (id) on delete cascade)")
		cur.execute("create table if not exists posters(id INT UNIQUE, title TEXT, \
original TEXT, detailed TEXT, thumbnail TEXT, profile TEXT)")
		cur.execute("create table if not exists alternates(id INT, alternateyear INT, \
alternatetitle TEXT, alternateid INT, foreign key (id) references moviestext (id) on delete cascade)")
		
		try:
			logging.info('Writing %s to database %s located in %s', 
					fulldata['imdb_title'], databasename, databasedir)
			cur.execute("insert into moviestext values(?, ?, ?, ?, ?, ?, ?, ?, \
?, ?, ?, ?, ?)", moviestextdata)		
		except lite.Error as e:
			logging.error('An error occured while writing into database: %s', e.args[0])
		else:		
			cur.execute("insert into moviesmisc values(?, ?, ?, ?, ?, ?, ?, ?)", moviesmiscdata)
			for datum in genredata:
				cur.execute("insert into genres values(?, ?)", datum)
			for datum in directordata:
				cur.execute("insert into directors values(?, ?)", datum)
			for datum in writerdata:
				cur.execute("insert into writers values(?, ?)", datum)
			for datum in characterdata:
				try:			
					cur.execute("insert into characters values(?, ?, ?)", datum)
				except lite.Error as e:
					datum = (datum[0], "Not Available", datum[1])
					cur.execute("insert into characters values(?, ?, ?)", datum)
			for datum in similardata:
				cur.execute("insert into similar values(?, ?, ?)", datum)
			for datum in posterdata:
				if isinstance(datum[0], int):
					try:
						cur.execute("insert into posters values(?, ?, ?, ?, ?, ?)", datum)
					except lite.Error as e:
						logging.error('Database error: %s', e.args[0])
			for datum in alternatedata:
				cur.execute("insert into alternates values(?, ?, ?, ?)", datum)

			logging.info('Written %s successfully to %s', fulldata['imdb_title'], databasename)

def totext(fulldata, outpath):
	"""
	Formats the data nicely and writes it to a text file.

	Keyword Arguments:
	fulldata		-- All the data extracted from RT and IMDB.
	outpath			-- The location of the text file to be written.

	I apologise for the crimes against readability committed in this function.

	"""
	sep_short = "=================="
	sep_long = "==========================================================="

	textgeneral = "\
\n{:^50}\n{:^50}\n\
{:>24} : {:<24}\n\
{:>24} : {:<24}\n\
{:>24} : {:<24}\n\
{:>24} : {:<24}\n\
{:>24} : {:<24}\n\
{:>24} : {:<24}\n\n\
{:^50}\n{}\n\n\
{:^50}\n{:^50}\n\n\
".format(
'General Info', sep_short, 
'Title', fulldata['imdb_title'], 
'Movie ID', fulldata['imdb_id'],
'Date of Release', fulldata['imdb_released'], 
'Censor Rating', fulldata['imdb_censor_rating'], 
'Genre', fulldata['imdb_genres'], 
'Runtime', fulldata['imdb_runtime'], 
'Plot', fulldata['imdb_plot'],
sep_long, sep_long)

	if isinstance(fulldata['rt_characters'], list):
		actors = ''
		for pair in fulldata['rt_characters']:
			actors = actors + '{:>24} - {:<24}'.format(pair['character'], pair['actor']) + '\n'
		textpeople = "\
{:^50}\n{:^50}\n\
{:>24} : {:<24}\n\
{:>24} : {:<24}\n\n\
{:^50}\n{}\n\
{:^50}\n{:^50}\n\n\
".format(
'People', sep_short, 
'Directors', fulldata['imdb_directors'], 
'Writers', fulldata['imdb_writers'],
'Actors', actors,
sep_long, sep_long)

	else:
		textpeople = "\
{:^50}\n{:^50}\n\
{:>24} : {:<24}\n\
{:>24} : {:<24}\n\
{:>24} : {:<24}\n\
\n{:^50}\n{:^50}\n\n\
".format(
'People', sep_short, 
'Directors', fulldata['imdb_directors'], 
'Writers', fulldata['imdb_writers'], 
'Characters', fulldata['imdb_characters'],
sep_long, sep_long)

	textrating = "\
{:^50}\n{:^50}\n\
{:>24} : {:<24}\n\
{:>24} : {:,}\n\
{:>24} : {:<24}\n\
{:>24} : {:<24}\n\n\
{:^50}\n{}\n\n\
{:^50}\n{:^50}\n\n\
".format(
'Rating Info', sep_short, 
'IMDb Rating', fulldata['imdb_rating'], 
'Votes', fulldata['imdb_votes'],
'Rotten Tomatoes Rating', str(fulldata['rt_tomatometer'])+'%', 
'Rotten Tomatoes Score', fulldata['rt_tomatorating'], 
'Consensus', fulldata['rt_consensus'], 
sep_long, sep_long)

	texttarantula = "\n\nThis text file was generated by Tarantula Movie Index.\n\
It can be used to index your movies, making navigating your collection simple :)\n\n\
Please don't edit the .json file, as doing so could lead to a global nuclear war.\
 You have been warned.\
\n"
	text = textgeneral + textpeople + textrating + texttarantula
	
	filename = common.cleanbeforewrite(fulldata['imdb_title']) + ' info.txt'
	outpathfile = os.path.join(outpath, filename)
	try:
		logging.info('Writing %s to %s', filename, outpath)
		with open(outpathfile, 'w') as f:
			f.write(text)
	except IOError as e:
		logging.error('Could not write to text because the folder %s does not exist.', outpath)
	else:
		logging.info('Written to %s successfully.', filename)
		
