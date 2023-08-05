#-*-coding: utf-8-*-
"""
Copyright 2011 Krishna Sundarram.
This program is distributed under the terms of the MIT License. 

The IMDB API is utilized to obtain data. 
Website: http://www.imdbapi.com/

Methods:
	queryapi()		-- Queries the imdbapi.com API

Classes:
	IMDB			-- Processes received data

This is imported by getdata and tarantula.

"""

import os
import sys
import urllib.request
from urllib.error import HTTPError, URLError
from socket import timeout
import json
import logging
#import pprint  # present for testing purposes
 
import common

def test(toprint):
	pp = pprint.PrettyPrinter(indent=4)
	pp.pprint(toprint)

class IMDB:

	"""
	Processes json object received from RT API call.

	Methods:
	movietitle()	-- Returns a string containing the Title of the movie.
	imdbid()		-- Returns an int containing the IMDB ID of the movie.
	censor_rating()	-- Returns a str containing the rating of the movie.
	runtime()		-- Returns an int containing the runtime of the movie.
	released()		-- Returns a str containing the release date of the movie.
	year()			-- Returns an int containing the release year of the movie.
	characters()	-- Returns a str containing the names of actors separated by commas.
	writers()		-- Returns a str containing the names of writers separated by commas.
	directors()		-- Returns a str containing the names of directors separated by commas.
	genres()		-- Returns a str containing the names of genres separated by commas.
	posterurl()		-- Returns a str containing the URL to download the poster of the movie.
	imdburl()		-- Returns a str containing the RottenTomatoes URL of the movie.
	rating()		-- Returns an int containing the IMDB rating of a movie.
	votes()			-- Returns an int containing the number of votes a movie received.
	plot()			-- Returns a str containing the plot of the movie.
	alldata()		-- Returns a dict containing all of the above.
	get_poster()	-- Retrieves the poster of the movie.

	"""

	def __init__(self, apidata):
		"""
		Constructor.

		Initializes the attribute self.data to the json object returned by the RT API.

		"""
		self.data = apidata

	def movietitle(self):
		"""Returns a string containing the Title of the movie."""
		try:
			return self.data['Title']
		except (KeyError, ValueError, TypeError):
			return 'Not Available'

	def imdbid(self):
		"""Returns an int containing the IMDB ID of the movie."""
		try:
			return int(self.data['ID'][2:])
		except (KeyError, ValueError, TypeError):
			return 'Not Available'

	def censor_rating(self):
		"""Returns a str containing the rating of the movie."""
		try:
			return self.data['Rated']
		except (KeyError, ValueError, TypeError):
			return 'Not Available'

	def runtime(self):
		"""Returns an int containing the runtime of the movie."""
		try:
			return self.data['Runtime']
		except (KeyError, ValueError, TypeError):
			return 'Not Available'

	def released(self):
		"""Returns a str containing the release date of the movie."""
		try:
			return self.data['Released']
		except (KeyError, ValueError, TypeError):
			return 'Not Available'

	def year(self):
		"""Returns an int containing the release year of the movie."""
		try:
			return int(self.data['Year'])
		except (KeyError, ValueError, TypeError):
			return 'Not Available'

	def characters(self):
		"""Returns a str containing the names of actors separated by commas."""
		try:
			return self.data['Actors']
		except (KeyError, ValueError, TypeError):
			return 'Not Available'

	def writers(self):
		"""Returns a str containing the names of writers separated by commas."""
		try:
			return self.data['Writer']
		except (KeyError, ValueError, TypeError):
			return 'Not Available'

	def directors(self):
		"""Returns a str containing the names of directors separated by commas."""
		try:
			return self.data['Director']
		except (KeyError, ValueError, TypeError):
			return 'Not Available'

	def genres(self):
		"""Returns a str containing the names of genres separated by commas."""
		try:
			return self.data['Genre']
		except (KeyError, ValueError, TypeError):
			return 'Not Available'

	def posterurl(self):
		"""Returns a str containing the URL to download the poster of the movie."""
		try:
			if not self.data['Poster'] == 'N/A':
				return self.data['Poster']
			else:
				return 'Not Available'
		except (KeyError, ValueError, TypeError):
			return 'Not Available'

	def imdburl(self):
		"""Returns a str containing the RottenTomatoes URL of the movie."""
		try:
			return 'http://www.imdb.com/title/' + self.data['ID']
		except (KeyError, ValueError, TypeError):
			return 'Not Available'

	def rating(self):
		"""Returns an int containing the IMDB rating of a movie."""
		try:
			return float(self.data['Rating'])
		except (KeyError, ValueError, TypeError):
			return 'Not Available'

	def votes(self):
		"""Returns an int containing the the number of votes a movie received."""
		try:
			return int(self.data['Votes'])
		except (KeyError, ValueError, TypeError):
			return 'Not Available'

	def plot(self):
		"""Returns a str containing the plot of the movie."""
		try:
			return self.data['Plot']
		except (KeyError, ValueError, TypeError):
			return 'Not Available'

	def alldata(self):
		"""Returns a dictionary containing all of the above."""
		alldata = {	"imdb_title": self.movietitle(),
					"imdb_id": self.imdbid(),
					"imdb_censor_rating": self.censor_rating(),
					"imdb_runtime": self.runtime(),
					"imdb_released": self.released(),
					"imdb_year": self.year(),
					"imdb_characters": self.characters(),
					"imdb_writers": self.writers(),
					"imdb_directors": self.directors(),
					"imdb_genres": self.genres(),
					"imdb_posterurl": self.posterurl(),
					"imdb_url": self.imdburl(),
					"imdb_rating": self.rating(),
					"imdb_votes": self.votes(),
					"imdb_plot": self.plot(),
					}
		return alldata

	def get_poster(self, outpath):
		"""
		Retrieves the poster of the movie.

		Keyword Arguments:
		outpath		-- The directory in which the poster must be placed.

		Output:
		Retrieves and stores an image in ../outpath/Title + 'IMDB.jpg'.

		Exceptions: IOError if the path does not exist.
		
		"""
		title = common.cleanbeforewrite(self.movietitle()) + ' IMDB.jpg'
		outpathimage = os.path.join(outpath, title)
		imageurl = self.posterurl()
		logging.info('Retrieving %s.', title)
		if not imageurl == 'Not Available':
			try:
				urllib.request.urlretrieve(imageurl, outpathimage)
			except (URLError, HTTPError) as e:
				logging.error('Failed because of %s\nImage URL: %s', e, imageurl)
			except IOError:
				logging.error('Failed because the folder %s does not exist.', outpath)
			else:
				logging.info('Retrieved %s sucessfully.', title)
		else:
			logging.error('Failed because image URL not available.')
	

def query_api(apiurl, moviename='', imdb_id=''):
	"""
	Queries the imdbapi.com API.

	Keyword Arguments:
	apiurl		-- The url of the RottenTomatoes API that returns movie data.
	moviename	-- The name of the movie. It should be separated by spaces.
	imdb_id			-- The id of the movie.

	Returns: 
	jsonresponse-- json object containing the data

	Exceptions:	HTTPError, URLError

	Side Effects: None

	"""
	moviename = moviename.replace(' ', '+')
	url = apiurl.format(moviename, imdb_id)
	numberofattempts = common.apiattempts
	for attempt in range(1, numberofattempts + 1):
		try:
			logging.info('IMDB attempt %s', str(attempt))
			response = urllib.request.urlopen(url, timeout=10).read().decode('utf-8')
		except (HTTPError, URLError) as error:
			logging.error('IMDB data of %s not retrieved because %s\nURL: %s', moviename, error, url)
		except timeout:
			logging.error('Socket timed out.\nURL: %s', url)
		else:
			logging.info('IMDB API access successful.')
			jsonresponse = json.loads(response)
			return jsonresponse
			break
