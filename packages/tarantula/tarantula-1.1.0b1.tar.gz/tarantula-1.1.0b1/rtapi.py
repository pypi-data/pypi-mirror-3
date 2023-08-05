#-*-coding: utf-8-*-
"""
Copyright 2011 Krishna Sundarram.
This program is distributed under the terms of the MIT License.

The Rotten Tomatoes API is utilized to obtain data.
Website: http://api.rottentomatoes.com/

Methods:
    queryapi()		-- Queries the RottenTomatoes API

Classes:
    RottenTomatoes	-- Processes received data

This is imported by getdata.

"""

import os
import sys
import urllib.request
from urllib.error import HTTPError, URLError
from socket import timeout
import json
import logging
#import pprint  # present for testing purposes

import trailer
import common


def test(toprint):
	pp = pprint.PrettyPrinter(indent=4)
	pp.pprint(toprint)


class RottenTomatoes:

	"""
	Processes json object received from RT API call.

	Methods:
	movietitle()	-- Returns a string containing the Title of the movie.
	imdbid()		-- Returns an int containing the IMDB ID of the movie.
	year()			-- Returns an int containing the year of release.
	censor_rating()	-- Returns a str containing the rating of the movie.
	runtime()		-- Returns an int containing the runtime.
	characters()	-- Returns a list containing {'character', 'actor'} dictionaries.
	consensus()		-- Returns a str the consensus of the movie.
	tomatometer()	-- Returns an int containing the RT score.
	tomatorating()	-- Returns a str containing the RT rating(eg 'Certified Fresh').
	similarurl()	-- Returns a str with the API URL to access the data about similar movies.
	posterurls()	-- Returns a dict with the URL to download the posters of the movie.
	rturl()			-- Returns a str containing the RottenTomatoes URL of the movie.
	trailerurl()	-- Returns a str containing the URL to retrieve the trailer.
	simtitles()		-- Returns a list with strs containing titles similar to the movie.
	simposters()	-- Returns a list with dicts containing poster urls of titles similar to the movie.
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
		try:
			return self.data['title']
		except (KeyError, TypeError):
			return 'Not Available'

	def imdbid(self):
		"""Returns the IMDB ID of the movie."""
		try:
			return int(self.data['alternate_ids']['imdb'])
		except (KeyError, TypeError):
			return 'Not Available'

	def year(self):
		"""Returns an int containing the year of release."""
		try:
			return int(self.data['year'])
		except (KeyError, TypeError):
			return 'Not Available'
	
	def censor_rating(self):
		"""Returns a str containing the rating of the movie."""
		try:
			return self.data['mpaa_rating']
		except (KeyError, TypeError):
			return 'Not Available'

	def runtime(self):
		"""Returns an int containing the runtime."""
		try:
			return self.data['runtime']
		except (KeyError, TypeError):
			return 'Not Available'

	def characters(self):
		"""Returns a list containing {'character', 'actor'} dictionaries."""
		try:
			characters = []
			for character in self.data['abridged_cast']:
				characters.append({'character': character['characters'][0], 'actor': character['name']})
			return characters
		except:
			return 'Actor info Not Available'

	def consensus(self):
		"""Returns a str the consensus of the movie."""
		try:
			return self.data['critics_consensus']
		except (KeyError, TypeError):
			return 'Not Available'

	def tomatometer(self):
		"""Returns an int containing the RT score."""
		try:
			return int(self.data['ratings']['critics_score'])
		except (KeyError, TypeError):
			return 'Not Available'
	
	def tomatorating(self):
		"""Returns a str containing the RT rating(eg 'Certified Fresh')."""
		try:
			return self.data['ratings']['critics_rating']
		except (KeyError, TypeError):
			return 'Not Available'

	def similar_url(self):
		"""Returns a str containing the API URL to access the data about similar movies."""
		try:
			return self.data['links']['similar']
		except (KeyError, TypeError):
			return 'Not Available'

	def posterurls(self):
		"""Returns a dict with the URL to download the posters of the movie."""
		try:
			return self.data['posters']
		except (KeyError, TypeError):
			return 'Not Available'

	def rturl(self):
		"""Returns a str containing the RottenTomatoes URL of the movie."""
		try:
			return self.data['links']['alternate']
		except (KeyError, TypeError):
			return 'Not Available'

	def trailerurl(self):
		"""Returns a str containing the URL to retrieve the trailer."""
		try:
			return 'Call explicitly instead'
#			return trailer.trailer_url(self.rturl())
		except:  # blanket except because this function can return many errors. Replace.
			return 'Not Available'

	def simtitles(self):
		"""
		Returns a list with tuples containing an int(imdbid) and a str(title).
		The tuples describe movies similar to the movie.

		"""
		try:
			return self.similartitles
		except (NameError, AttributeError):
			return 'Not Available'

	def simposters(self):
		"""Returns a list with dicts containing poster urls of titles similar to the movie."""
		try:
			return self.similarposters
		except (NameError, AttributeError):
			return 'Not Available'

	def alldata(self):
		"""Returns a dictionary containing all of the above."""
		alldata = {	"rt_title": self.movietitle(),
					"rt_id": self.imdbid(),
					"rt_year": self.year(),
					"rt_censor_rating": self.censor_rating(),
					"rt_runtime": self.runtime(),
					"rt_characters": self.characters(),
					"rt_consensus": self.consensus(),
					"rt_tomatometer": self.tomatometer(),
					"rt_tomatorating": self.tomatorating(),
					"rt_posterurl": self.posterurls(),
					"rt_url": self.rturl(),
					"rt_trailerurl": self.trailerurl(),
					"rt_similartitles": self.simtitles(),
					"rt_similarposters": self.simposters(),
					}
		return alldata
	
	def get_poster(self, outpath, quality):
		"""
		Retrieves the poster of the movie.

		Keyword Arguments:
		outpath		-- The directory in which the poster must be placed.
		quality		-- The quality of the image requested.

		Output:
		Retrieves and stores an image in ../outpath/Title + 'RT.jpg'.
		Quality options:
			thumbail = 60x90 px
			profile  = 120x180 px
			detailed = 180x270 px
			original = Between 250x380 px and 500x750 px (It really isn't consistent)

		Exceptions: IOError if the path does not exist.
		
		"""
		title = common.cleanbeforewrite(self.movietitle()) + ' RT.jpg'
		outpathimage = os.path.join(outpath, title)
		imageurl = self.data['posters'][quality]
		if not imageurl == 'Not Available':
			try:
				logging.info('Retrieving %s.', title)
				urllib.request.urlretrieve(imageurl, outpathimage)
			except (URLError, HTTPError) as e:
				logging.error('Failed because of %s\nImage URL: %s', e, imageurl)
			except IOError:
				logging.error('Failed because the folder %s does not exist.', outpath)
			else:
				logging.info('Retrieved %s sucessfully.', title)
		else:
			logging.error('Failed because image URL not available.')
	

def query_api(apiurl, moviename):
	"""
	Queries the RT API.

	Keyword Arguments:
	apiurl		-- The url of the RottenTomatoes API that returns movie data.
	moviename	-- The name of the movie. It should be separated by spaces.

	Returns:
	jsonresponse-- json object containing the data

	Exceptions:	HTTPError, URLError

	Side Effects: None

	"""
	url = apiurl + moviename.replace(' ', '%20') + common.rt_apikey
	numberofattempts = common.apiattempts
	for attempt in range(1, numberofattempts + 1):
		try:
			logging.info('RottenTomatoes attempt %s', str(attempt))
			response = urllib.request.urlopen(url, timeout=10).read()
		except (HTTPError, URLError) as error:
			logging.error('RottenTomatoes data of %s not retrieved because %s\nURL: %s', moviename, error, url)
		except timeout:
			logging.error('Socket timed out.\nURL: %s', url)
		else:
			logging.info('RottenTomatoes API access successful.')
			jsonresponse = json.loads(response.decode('utf-8'))
			return jsonresponse
			break
