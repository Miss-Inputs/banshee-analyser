#Task list:
#	- Inconsistent total discs for same albumid (or album + artist), inconsistent total tracks on
#		each disc
#	- Incosistent year for same album
#	- Maintenance?
#		- Will need to add parameter to get_db() to not create copy, throw error instead if
#			Banshee is running
#		- Delete from corealbums with no coretracks with that albumid? (Is this safe)
#		- Delete from coreartists with no coretracks with that artistid?
#		- Delete old media sources (e.g. USB devices no longer in use?)
#		- See also cleanup.sql for other stuff
#		- Vacuum
#		- Files what don't exist (particularly in coreremovedtracks... what a mess)
#	- GUI interface my dudette
#	- I guess I could probably clean up some duplicated code, but I don't feel like it
#	- View where Banshee DB differs from song tags (use taglib)
#	- Fiddle with album artwork, report where non-existent, make sure Banshee sees it
#	- ID3 standards violations (kid3 knows about these, I wonder if I can use its DBus API or command line interface)

from core import *

if __name__ == "__main__":
	
	conn = get_db()
	print(query(conn, 'SELECT * FROM coretracks WHERE primarysourceid = 1 AND does_uri_exist(uri)'))
	
	#mode = 's'
	mode = input('Enter mode: ')
	
	if mode == 'query':
		sql = input('Enter query: ')
		results = query(conn, sql)
		for row in results:
			print(row)
	elif mode.startswith('d'):
		dupes = get_playlist_duplicates(conn)
		for dupe in dupes:
			print('{0}: {1} ({2}) appears {3} times'.format(dupe['playlistName'], get_readable_track_by_id(conn, dupe['TrackID']), dupe['TrackID'], dupe['count']))
	elif mode.startswith('s'):
		get_same_names(conn)
	else: 
		print('bleh')