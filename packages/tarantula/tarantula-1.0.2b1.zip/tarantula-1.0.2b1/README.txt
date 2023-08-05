
=====================
tarantula
=====================

Description
-----------------

Tarantula crawls your movie directory, and retrieves info, 
posters and trailer of the movies present from the International 
Movie Database(IMDb) and RottenTomatoes.com. It also creates a 
local database of the retrieved info.

Information obtained includes Plot, Director, Actors, IMDb Rating, 
TomatoMeter, etc.

The sqlite database can then be searched using sql commands such 
as the following, which shows you all the movies directed by 
Christopher Nolan.

``select title, director from moviestext, directors where 
moviestext.id = directors.id and director = 'Christopher Nolan'``

Version
-----------------
1.0.2b1

Modules
-----------------
 * getmoviedata - Gets info about a movie and stores in the 
   form of text, json and an sqlite DB.
 * tarantula - Recursively searches a directory, identifying 
   movies. Then calls getmoviedata.
 * correcter - In case the info is wrong, the user can correct it.

How to Use
-----------------
Extract the .tar/.zip file and run this from the command line:
``python3 setup.py install``

For help on usage, run the following from the command line:
tarantula.py --help
getmoviedata.py --help
correcter.py --help

Licensing
-----------------
MIT License. Refer License.txt

Notes
-----------------
Only tested on Python 3.2

List of Authors
-----------------
Krishna Sundarram


Bug Reports/ Feature Requests can be sent to krishna.sundarram@gmail.com

Readme written on 10th January 2012.
