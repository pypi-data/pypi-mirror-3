#-*-coding = 'utf-8' -*-
"""
Copyright 2011 Krishna Sundarram.
This program is distributed under the terms of the MIT License.

Methods:
	trailer_url()	-- Returns as str the URL from which the trailer can be downloaded
	download_trailer()-- Downloads trailer
	trailer()		-- Calls both of the above functions

To use:
import os
from trailer import trailer
trailer('Hugo', 'http://www.rottentomatoes.com/m/hugo/trailers/', os.getcwd())
"""

import urllib.request
from urllib.error import HTTPError, URLError
from socket import timeout
import os
import xml.dom.minidom as dom
import re
import logging
import shutil


def trailer_url(url):
	"""
	Retrieves the URL from which the  trailer can be downloaded.

	Keyword Arguments:
	url			-- the RottenTomatoes URL of the movie.

	Procedure: 
	Queries the page url/trailers/ where the video is present
	In the div with class="video", there is an url that leads to VideoDetective.net
	This url has 3 parameters which uniquely identify the video:
		- customerid: It is the ID that corresponds to rt.com. It is usually 300120.
		- playerid: Unknown what exactly it is. It is usually 351. 
		- publishedid: Uniquely identifies a video.
	Note that even if the first two parameters change, this function will still work.

	The three parameters are plugged into the following url(first_url)
	http://www.videodetective.net/flash/players/flashconfiguration.aspx?customerid={}&playerid={}&publishedid={}
	I found this url by following the earlier url. 
	That leads to a flash player on videodetective.net
	If you urlopen that, you will get a small .swf file, less than 100kB.
	The tool cws2swf makes it human readable.
	Upon analysis of that, the above url is extracted.
	This method is thanks to an amazing guy on stackoverflow.

	When the first_url is opened, an xml file is present.
	The url present in the <file> tag is extracted. It becomes second_url.

	When the second_url is opened, an xml file is present.
	The url present in the <location> tag is extracted. It becomes third_url.

	The third_url should start with http://cdn.videodetective.net/
	This is opened and read into a file specified by outpath.
	This is not done in this function.
	
	The urlopen of the RottenTomatoes site only works if the headers are changed to chrome.
	The urlopen of third_url does not work for a normal browser header.
	Header should be Python's urllib user agent in that case.

	"""
	headers ={
	'Firefox': { 'User-Agent' : 'Mozilla/4.0 (compatible; MSIE 5.5; Windows NT)' },
	'Chrome': {'User-Agent': 'Mozilla/5.0 (Windows NT 6.0; WOW64) AppleWebKit/534.24 (KHTML, like Gecko) Chrome/11.0.696.16 Safari/534.24'},
	}

	req = urllib.request.Request(url + 'trailers/', b'', headers['Chrome'])
	try:
		logging.info('Accessing URL %s', url + 'trailers/')
		resp = str(urllib.request.urlopen(req, timeout=10).read())
	except (HTTPError, URLError) as error:
		logging.error('HTTP/URL Error: %s \nURL: %s', error, url)
	except timeout:
		logging.error('Socket timed out.\nURL: %s', url)
	else:
		logging.info('Trailer page access successful')

		param_expr = re.compile('<div class="video".*?</div>.*?</div>.*?</div>', re.DOTALL)
		param_res = param_expr.findall(resp)[0]

		customerid_expr = re.compile('customerid=[0-9]*')
		playerid_expr = re.compile('playerid=[0-9]*')
		publishedid_expr = re.compile('publishedid=[0-9]*')
		customerid = customerid_expr.search(param_res).group()[11:]
		playerid = playerid_expr.search(param_res).group()[9:]
		publishedid = publishedid_expr.search(param_res).group()[12:]
		attributes = {"customerid":customerid, "playerid": playerid, "publishedid":publishedid}
	
		first_url = 'http://www.videodetective.net/flash/players/flashconfiguration.aspx?customerid={}&playerid={}&publishedid={}'
		first_url = first_url.format(attributes['customerid'], attributes['playerid'], attributes['publishedid'])
		req = urllib.request.Request(first_url, b'', headers['Chrome'])
		try:
			logging.info('Accessing first url: %s', first_url)
			resp = urllib.request.urlopen(req, timeout=10).read().decode('utf-8')
		except (HTTPError, URLError) as error:
			logging.error('HTTP/URL Error: %s \nURL: %s', error, first_url)
		except timeout:
			logging.error('Socket timed out.\nURL: %s', first_url)
		else:
			logging.info('First access successful.')
		
			first_xml = dom.parseString(resp)
			xmltag = first_xml.getElementsByTagName('file')[0].toxml()
			xmldata = xmltag.replace('<file>', '').replace('</file>', '').replace("&amp;", "&")
	
			second_url = xmldata
			req = urllib.request.Request(second_url, b'', headers['Chrome'])
			try:
				logging.info('Accessing second url: %s', second_url)
				resp = urllib.request.urlopen(req, timeout=10).read().decode('utf-8')
			except (HTTPError, URLError) as error:
				logging.error('HTTP/URL Error: %s \nURL: %s', error, second_url)
			except timeout:
				logging.error('Socket timed out.\nURL: %s', second_url)
			else:
				logging.info('Second access successful.')
		
				second_xml = dom.parseString(resp)
				xmltag = second_xml.getElementsByTagName('location')[0].toxml()
				xmldata = xmltag.replace('<location>', '').replace('</location>', '').replace("&amp;", "&")
				third_url = xmldata

				return third_url


def download_trailer(title, outpath, downloadurl):
	"""
	Downloads trailer from the URL specified in downloadurl.

	Keyword Arguments:
	title		-- The title of the movie.
	outpath		-- The directory in which the file should be written.
	downloadurl	-- The cdn.videodetective.net URL which is the download location.

	This does not work if the user agent is changed to Chrome or Firefox.
	Python's urllib user agent is used.
	
	THe video url is opened and the trailer is downloaded.
	It is written to outpath.
	If the trailer is a dummy, ie, size ~ 10kB, move it to metadata and return 
	False. Else return True.
	
	"""
	try:
		logging.info('Retrieving trailer for %s', title)
		resp = urllib.request.urlopen(downloadurl).read()
	except (HTTPError, URLError) as e:
		logging.error('Retrieving video failed because of %s\nURL: %s', e, downloadurl)
	except timeout:
		logging.error('Socket timed out.\nURL: %s', downloadurl)
	else:	
		outpathfile = os.path.join(outpath, common.cleanbeforewrite(title) + ' trailer.mp4')
		try:
			with open(outpathfile, 'wb') as f:
				f.write(resp)
		except IOError as e:
			logging.error('Retrieving video failed because of %s', e)
		else:
			logging.info('Trailer retrieved for %s and written successfully to %s', title, outpath)
			trailersize = os.path.getsize(outpathfile)
			if trailersize < 100*1024:
				newoutpath = os.path.join(outpath, 'metadata', common.cleanbeforewrite(title) + ' trailer.mp4')
				shutil.copy2(outpathfile, newoutpath)
				return False
			else:
				return True

def trailer(title, outpath, url):
	"""
	Retrieves the trailer of a movie using scraping.

	Keyword arguments:
	title		-- The title of the movie.
	outpath		-- The directory in which the file should be written.
	url			-- The RottenTomatoes url of the movie.

	There are many reasons this method could fail.
	Also, any changes to the RottenTomatoes site or VideoDetective will break it.

	"""
	downloadurl = trailer_url(url)	
	download_trailer(title, outpath, downloadurl)
