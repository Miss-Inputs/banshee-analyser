from core import *

def main():
	def query(db, sql, * params):
		cursor = db.execute(sql, params)
		columns = [x[0] for x in cursor.description]

		return [dict(zip(columns, row)) for row in cursor]

	def query_onecol(db, sql, * params):
		cursor = db.execute(sql, params)
		return [row[0] for row in cursor]

	def query_first(db, sql, * params):
		cursor = db.execute(sql, params)
		columns = [x[0] for x in cursor.description]
		row = cursor.fetchone()
		if row is None:
			return None

		return dict(zip(columns, row))

	def banshee_is_running():
		"""
		This relies on you having the MPRIS plugin enabled, but if you don't, that 
		is your own problem
		It seems you can't check for the org.bansheeproject.Banshee service because
		that is always there
		"""
		bus = dbus.SessionBus()
		for service in bus.list_names():
			if service == 'org.mpris.MediaPlayer2.banshee':
				return True

		return False

	def get_track_by_id(db, track_id):
		return query_first(db, 'SELECT * FROM coretracks WHERE trackid = ?', track_id)

	def get_artist_name(db, artist_id):
		if not hasattr(get_artist_name, 'cache'):
			get_artist_name.cache = {}
		if artist_id in get_artist_name.cache:
			return get_artist_name.cache[artist_id]

		artist = query_first(db, 'SELECT name FROM coreartists WHERE artistid = ?', artist_id)
		get_artist_name.cache[artist_id] = artist['Name']
		return artist['Name']

	def get_album_name(db, album_id):
		if not hasattr(get_album_name, 'cache'):
			get_album_name.cache = {}
		if album_id in get_album_name.cache:
			return get_album_name.cache[album_id]

		album = query_first(db, 'SELECT title FROM corealbums WHERE albumid = ?', album_id)
		get_album_name.cache[album_id] = album['Title']
		return album['Title']

	def get_readable_track_by_id(db, track_id):
		track = get_track_by_id(db, track_id)
		if track is None:
			return None
		artist = query_first(db, 'SELECT * FROM coreartists WHERE artistid = ?', track['ArtistID'])
		return '{1} - {0}'.format(track['Title'], artist['Name'])

	def get_playlist_duplicates(db):
		playlists = query(db, 'SELECT * FROM coreplaylists WHERE primarysourceid = 1')
		dupes = []
		for playlist in playlists:
			sql = 'SELECT trackid, COUNT(*) as count FROM coreplaylistentries WHERE\
			 playlistid = ? GROUP BY trackid ORDER BY count DESC'
			entries = query(db, sql, playlist['PlaylistID'])
			for dupe in filter(lambda x: x['count'] != 1, entries):
				dupe['playlistName'] = playlist['Name']
				dupes.append(dupe)

		return dupes

	def get_same_names(db):
		sql = 'SELECT title FROM coretracks WHERE primarysourceid = 1\
		 GROUP BY ensure_singular(title) HAVING COUNT(ensure_singular(title)) > 1'
		names = query_onecol(db, sql)
		for name in names:
			sql = 'SELECT title, artistid, albumid FROM coretracks WHERE\
			 primarysourceid = 1 AND ensure_singular(title) = ensure_singular(?)'
			tracks = query(db, sql, name)
			print('Name: ' + name)
			for track in tracks:
				artist = get_artist_name(db, track['ArtistID'])
				album = get_album_name(db, track['AlbumID'])
				print('\t{0} - {1} - {2}'.format(artist, album, track['Title']))

	def get_db(readonly=True):	
		banshee_db_path = '{0}/.config/banshee-1/banshee.db'.format(expanduser('~'))
		if banshee_is_running():
			print('Banshee is running so we will avoid messing with its locking by having our own copy')
			new_path = copy2(banshee_db_path, '/tmp/banshee-analysis.db')
			path = 'file:{0}?mode=ro'.format(new_path)
		else:
			path = 'file:{0}?mode={1}'.format(banshee_db_path, 'ro' if readonly else 'rw')
		conn = sqlite3.connect(path, uri=True)
		conn.create_function("ensure_singular", 1, ensure_singular)
		return conn

	def is_equal_number_insensitive(s1, s2):
		#This won't return true if there's multiple plurals
		#(e.g. "cats and dogs" != "cat and dog". Not much I can do about it that I can see
		return p.compare(s1.lower(), s2.lower())

	def ensure_singular(s):
		if p.singular_noun(s):
			return p.singular_noun(s)

		return s

	def get_album_aggregate_rating(db, album_id):
		sql = 'SELECT AVG(rating) as average_rating, COUNT(*) as track_count,\
		 TOTAL(rating) as total_rating FROM coretracks WHERE albumid = ? AND primarysourceid = 1'
		return query_first(db, sql, album_id)

	def get_albums_with_rating_aggregates(db, track_count_threshold=0):
		#Note that there is a Rating column in corealbums that doesn't do anything
		#Sometimes, corealbums will contain stuff that doesn't even have any tracks associated
		#with it (because it used to exist and now it doesn't), or maybe they're tracks that aren't
		#in primarysourceid = 1, which isn't a column in corealbums so there's not much that can be
		#done until we look at coretracks anyway
		#Hmm.... would it be better to look at coretracks grouped by albumid?
		albums = query(db, 'SELECT albumid, artistname, title FROM corealbums')
		def __append_rating(album):
			return dict(album, ** get_album_aggregate_rating(db, album['AlbumID']))
		#Can I just merge the things into a big SQL? Maybe, maybe not, cbf tbh fam
		albums_with_rating = [__append_rating(album) for album in albums]
		return [album for album in albums_with_rating if album['track_count'] > track_count_threshold]

	def get_top_albums_by_average_rating(db, amount, track_count_threshold=0):
		#TODO Make this more generic, so we can use total_rating as well as average_rating
		#TODO Bottom 10 (exclude stuff with no tracks / no ratings)
		albums = get_albums_with_rating_aggregates(db, track_count_threshold)
		return sorted(albums, key=lambda album: album['average_rating'], reverse=True)[:amount]

	def get_duplicate_album_ids(db):
		#TODO Exclude where the only other duplicate has no tracks associated with it
		sql = 'SELECT albumid, artistname, title, (SELECT COUNT(*) FROM coretracks t\
		 WHERE t.albumid = m.albumid AND primarysourceid = 1) AS track_count FROM corealbums m\
		 WHERE artistname || title IN\
		 (SELECT artistname || title FROM corealbums\
		 GROUP BY artistname, title HAVING COUNT(*) > 1)\
		 ORDER BY artistname || title'
		return query(db, sql)

	def get_duplicate_track_numbers(db):
		sql = 'SELECT t.title as title, m.title as album, tracknumber, disc FROM coretracks t JOIN corealbums m\
		 USING (albumid) WHERE albumid || disc || \'-\' || tracknumber IN \
		 (SELECT albumid || disc || \'-\' || tracknumber FROM coretracks WHERE primarysourceid = 1\
		 GROUP BY albumid, disc, tracknumber HAVING COUNT(*) > 1) AND primarysourceid = 1\
		 AND album <> \'[non-album tracks]\' AND t.albumid IS NOT NULL'
		return query(db, sql)

	def get_missing_track_total(db):
		return query(db, 'SELECT t.title as title, m.title as album, t.disc, t.tracknumber\
		 FROM coretracks t JOIN corealbums m USING (albumid) WHERE trackcount = 0 AND\
		 albumid IS NOT NULL AND album <> \'[non-album tracks]\' AND primarysourceid = 1')

	def get_missing_disc_total(db):
		return query(db, 'SELECT t.title as title, m.title as album, t.disc, t.tracknumber\
		 FROM coretracks t JOIN corealbums m USING (albumid) WHERE disccount = 0 AND\
		 albumid IS NOT NULL AND album <> \'[non-album tracks]\' AND primarysourceid = 1')

	def get_missing_track_number(db):
		return query(db, 'SELECT t.title as title, m.title as album, t.disc\
		 FROM coretracks t JOIN corealbums m USING (albumid) WHERE tracknumber = 0 AND\
		 albumid IS NOT NULL AND album <> \'[non-album tracks]\' AND primarysourceid = 1')

	def get_missing_disc_number(db):
		return query(db, 'SELECT t.title as title, m.title as album, t.tracknumber FROM coretracks t\
		 JOIN corealbums m USING (albumid) WHERE disc = 0 AND\
		 albumid IS NOT NULL AND album <> \'[non-album tracks]\' AND primarysourceid = 1')

	def get_missing_year(db):
		return query(db, 'SELECT t.title as title, m.title as album, t.disc, t.tracknumber\
		 FROM coretracks t JOIN corealbums m USING (albumid) WHERE t.year = 0 AND\
		 albumid IS NOT NULL AND primarysourceid = 1 ORDER BY album')

	def get_missing_genre(db):
		return query(db, 'SELECT t.title as title, m.title as album, t.disc, t.tracknumber\
		 FROM coretracks t JOIN corealbums m USING (albumid) WHERE genre IS NULL AND\
		 albumid IS NOT NULL AND primarysourceid = 1')

	def get_inconsistent_album_year(db):
		return query(db, 'SELECT t.title as title, t.albumid, m.title as album FROM coretracks t\
		 JOIN corealbums m USING (albumid) WHERE primarysourceid = 1 GROUP BY t.albumid\
		 HAVING COUNT(DISTINCT t.year) > 1 ORDER BY album')

	def get_most_profilic_artists(db, amount):
		return query(db, 'SELECT a.name, COUNT(*) as track_count FROM coretracks t\
		 JOIN coreartists a USING (artistid) WHERE t.primarysourceid = 1 GROUP BY t.artistid\
		 ORDER BY track_count DESC LIMIT ?', amount)

if __name__ == "__main__":
	main()
