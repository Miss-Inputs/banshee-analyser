I'll put what tables do which as I find out, based on my own personal experience with poking around in Sqliteman on my own system with my own Banshee database. I also need to figure out how to see BLOBs in Sqliteman to see what I can do with them
One day I'll get around to reading the Banshee source code to know for sure what all of this does instead of just guessing, and then it will become a useful resource for all  

albumartwriter  
I'll need to look at Banshee source to know what this does  
	- AlbumID: Foreign key to corealbums albumid  
	- SavedOrTried: Some number from 1-3? Who knows  
	- LastUpdated: Seems like you're supposed to use datetime(LastUpdated, 'unixepoch') with this  

anonymoususagedata  
Secret evil telemetrics  
	- MetricName: Some kind of category  
	- Stamp: When it was collected I guess (Unix epoch)  
	- Value: Dependent on MetricName, e.g. when metric = "Banshee/LongSqliteCommand", it seems to be the first line indicating how long this SQL command took to run and then the rest is the actual SQL command that was executed here  
	- Id: Just an incrementing number  

bookmarks  
This is where the bookmarks go when you do Tools > Bookmarks > Add Bookmark  
	- BookmarkId: Primary key  
	- Position: Time within the song where the bookmark is, in milliseconds from the start  
	- CreatedAt: Unix timestamp for when you added the bookmark  
	- Type: ? (It's just null)  
	- TrackId: Foreign key to coretracks > trackid indicating the track for which you added the bookmark, if this doesn't exist then this row is junk and can be deleted  

corealbums  
Information for each album. I need to find out if it's safe to remove rows here when the albumID isn't referenced anywhere in coretracks
Sometimes you will have two entries in corealbums for the same album artist/album title combination and there's no particular reason why that would happen that I can think of  
	- AlbumID: Primary key  
	- ArtistID: Foreign key to coreartists artistid  
	- TagSetID: ?  
	- MusicBrainzID: ?  
	- Title: Name of the album (Unknown Album is null)  
	- TitleLowered: Title in lowercase (if Title is null this is "unknown album")  
	- TitleSort: Version of album title used for sorting (as entered in Sort Album field in song properties)  
	- TitleSortKey: blob  
	- ReleaseDate: ?  
	- Duration: ?  
	- Year: ?  
	- IsCompilation: 0 or 1 for the compilation box being ticked  
	- ArtistName: Name of artist (seemingly identical to looking up ArtistID in coreartists and getting back Name column)  
	- ArtistNameLowered: ArtistName in lowercase  
	- ArtistNameSortKey: blob  
	- Rating: ?  
	- ArtworkID: Something among the lines of "album-" + hexadecimal string, could be related to coverartdownloads?  

coreartists  
Information (but not much) for each artist. In the same vein as corealbums, it'd be good to know if I can delete stuff where the artistid isn't referenced anywhere  
	- ArtistID: Primary key  
	- TagSetID: ?  
	- MusicBrainzID: ?  
	- Name: Name of the artist (Unknown Artist is null)  
	- NameLowered: Name in lowercase (null > "unknown artist")  
	- NameSort: Version of name used for sorting (as entered in Sort Artist field in song properties)  
	- NameSortKey: blob  
	- Rating: ?  

corecachemodels  
?  
	- CacheID: Incrementing number, seems to be primary key  
	- ModelID: Something like "MusicLibrarySource-Library-AlbumInfo" or "SmartPlaylistSource-71-DatabaseYearInfo" or I dunno  

coreconfiguration  
Looks like it's used for storing key/value pairs  
	- EntryID: Primary key, incrementing number  
	- Key, Value: Obvious  
	What's probably more interesting is the keys (i.e. the possible values in the key column), and the associated values (e.g. the value in the Value column for that row where the Key is that), some of them seem to just be version numbers and I don't know why they need to be stored (maybe to make sure the database is compatible with future Banshee versions?) but let's take a look anyway, and see what the values are on my system at least:  
	- DatabaseVersion: Value is some number, I have 45  
	- MetadataVersion: I have 8  
	- SortKeyLocale: Appears to be a country code thing that decides sorting stuff (I have "en-AU")  
	- AlbumArtWriter.Version: I have 2  
	- SmartPlaylistVersion: I have 1  
	- HaveCreatedSmartPlaylists.MusicLibrarySource-Library: I have "True"  
	- MusicLibraryLocationMigrated: I have 1  
	- MusicImportSettingsMigrated: I have 1  
	- HaveCreatedSmartPlaylists.VideoLibrarySource-VideoLibrary: I have "True"  
	- VideoImportSettingsMigrated: I have 1  
	- InternetRadio.LegacyXspfMigrated: I have "True"  
	- InternetRadio.SystemXspfLoaded: I have "True"  
	- plugins.play_queue.current_offset: I have 0, maybe if I fiddle with the Play Queue this will be different?  
	- Podcast.Version: I have 7  
	- plugins.play_queue.current_track: I have 0  
	- last_cover_art_scan: I have "16/04/2017 12:30:53 PM", and it's interesting that this is a string when everywhere else Banshee stores dates as a Unix timestamp  
	- MetadataFixupGeneration.dupe-artist: I have 11  
	- MetadataFixupGeneration.dupe-album: I have 5  
	- MetadataFixupGeneration.dupe-genre: I have 3  
	- AnonymousUsageData.Userid: Some UUID which may well identify me because it's called a user ID... is that really anonymous? :p  
	- AnonymousUsageData.LastPostStamp: Another date string, I have "18/03/2017 10:22:23 AM". Perhaps that's the last time the stuff in anonymoususagedata got sent to the Banshee devs?  
	- amazonmp3.smart_playlist_version: I have 1  

coreplaylistentries  
This contains a row for every single item in a (manual) playlist  
	- EntryID: Primary key  
	- PlaylistID: Foreign key to coreplaylists > playlistid, if this doesn't exist in coreplaylists then this row is junk and should be able to be deleted  
	- TrackID: Foreign key to coretracks > trackid, if this doesn't exist in coretracks then this row is junk and should be able to be deleted  
	- ViewOrder: ? (seems to be always 0)  
	- Generated: ? (seems to be always 0)  

coreplaylists  
Contains each manual playlist (but not the entries, see coreplaylistentries) and also the Play Queue  
	- PrimarySourceID: Foreign key to coreprimarysources > primarysourceid, null for Play Queue, otherwise if this doesn't exist then this row is junk and should be able to be deleted  
	- PlaylistID: Primary key, 1 = play queue  
	- Name: The actual name that the user sees and enters  
	- SortColumn: I guess what this is sorted by, I have -1 for all of them so I dunno  
	- SortType: Seems to be 0 or 1 (could this be related to that manual ordering mode that it talks about when telling you off for trying to sort by a column?)  
	- Special: 1 or 0 (Play queue is 1 and the rest are 0 by the looks of it, so this would be a boolean that says the play queue is special)  
	- CachedCount: ? Just some number when primarysourceid = 1 and null otherwise or 0 if play queue, from what I can see  
	- IsTemporary: ? I only see 0  

coreprimarysources  
This identifies the music library, the video library, podcast libraries etc, as well as any portable devices you ever plug in  
	- PrimarySourceID: Primary key, 1 is hardcoded as being the music library (or at least I hope so because I've been relying on that being the case this whole time), and if I'm correct about that then 2 = video library, 3 = filesystem queue, 4 = internet radio, 5 = podcasts; for me the audiobook library is 261 which doesn't seem to me like it was hardcoded  
	- StringID: Can be something like "MusicLibrarySource-Library" if it's the music library etc, the other builtin ones are "VideoLibrarySource-VideoLibrary", "FileSystemQueueSource-file-system-queue", "InternetRadioSource-internet-radio", "PodcastSource-PodcastLibrary" and "AudiobookLibrarySource-AudiobookLibrary"; the other ones refer to portable devices and are stuff like "MassStorageSource-/devices/pci0000:00/0000:00:14.0/usb1/1-2/1-2:1.0/host12/target12:0:0/12:0:0:0/block/sdc/sdc1" and it'd be good to be able to decode that garbage so I can reliably tell if this device even still exists or not  
	- CachedCount: ? Either some number or null but most often 0  
	- IsTemporary: ? I only see 0  

coreremovedtracks  
Tracks that you remove go to here, I guess it's so Banshee knows not to import them again  
	- TrackID: This doesn't look sequential, but I guess it's the primary key? Or maybe it's what the TrackID was when it was in coretracks before it was removed?  
	- Uri: Location of the file as a file:// URI, e.g. "file:///home/megan/Music/some%20sucky%20song.ogg"  
	- DateRemovedStamp: Unix timestamp indicating when it was removed  

coreshufflermodifications  
???  
	- ShufflerId: ? I only see 1, but it's probably a foreign key to coreshufflers > shufflerid  
	- TrackID: I would imagine foreign key to coretracks > trackid  
	- LastModifiedAt: Unix timestamp that means something (probably)  
	- ModificationType: ? Only see 1  

coreshufflers  
???? I only have one row here  
	- ShufflerId: I guess it's the primary key  
	- Id: My one row's value is "PlayQueueSource-1"  

coreshuffles  
???? Is this written to every time a song is skipped or ends and a new one is played when shuffle mode is on or something? Maybe it's to stop the same song coming up in shuffle all the time  
	- ShufflerId: ?? You'd think it'd be a foreign key to coreshufflers > shufflerid but I can only see 0 in here which doesn't exist there  
	- TrackID: Foreign key to coretracks > trackid  
	- LastShuffledAt: Timestamp for... when the track was shuffled I guess  

coresmartplaylistentries  
This is essentially the same as coreplaylistentries, except it's for smart playlists, and as such instead of the PlaylistID column you have SmartPlaylistID which is a foreign key to coresmartplaylists > smartplaylistid. Not much point describing the rest  

coresmartplalylists  
Where all the smart playlists get stored (but not the entries in them). There won't be anything for portable devices, since those are converted to manual playlists on the device when synchronized  
	- PrimarySourceID: Same as coreplaylists  
	- SmartPlaylistID: Primary key  
	- Name: Same as coreplaylists  
	- Condition: Hoo boy! Now we're getting interesting. It's an XML document that contains all the smart playlist parameters, as an example (90's Music):  
	<request><query banshee-version="1"><and><greaterThanEquals><field name="year" /><int>1990</int></greaterThanEquals><lessThanEquals><field name="year" /	><int>1999</int></lessThanEquals></and></query></request>  
	If I didn't know any better, I'd say going by this XML format Banshee supports much more advanced conditions than what the GUI allows you to create. Just here we're saying the year is greater than or equal to 1990 and also less than or equal to 1999. But it just struck my eye that those two year conditions are contained within an "and" element, so does this mean in theory you could have complex logical conditions with this and (that or stuff)? Well, who knows.  
	It'd be good to have a complete guide on all the fields and operators that Banshee understands, but until then, it should be straightforward enough for a human to read it, and slightly less straightforward but still overall straightforward for a human to make a program that parses it. Note that when you have smart playlists that have conditions like "Songs that are in this other playlist", that other playlist will be referred to with a playlistID from the coreplaylists table.  
	If you don't have a filter (i.e. the "Match any/all of these conditions" box is unchecked) and you're just using a smart playlist to do things like "limit to X songs by this order", this will be null  
	- OrderBy: If you have the box ticked that says "Limit by x ys sorted by z", this is the z there, e.g. for Top 50 Played this is "PlayCount-DESC"; I have also seen stuff like "Rating-DESC" and "Score-DESC"  
	- LimitNumber: The number of stuff designated by LimitCriterion to limit to, so if LimitCriterion is "songs" and LimitNumber is 100 then it's limited to 100 songs, e.g. for Top 50 Played this is 50  
	- LimitCriterion: Something like "songs" or "GB", depending on what we're limiting by  
	- CachedCount: I am as confused as I am with the coreplaylists column of the same name  
	- IsTemporary: Same here  
	- IsHiddenWhenEmpty: Huh, I guess some of them hide when empty? I have a 1 for the Favorites playlist (which I can tell is inbuilt because of the spelling), but it's not empty so I don't know if it actually means that or not, they're mostly 0 anyway  

coretracks  
This is the fun part, it's where all the tracks are stored (funnily enough), including those on portable devices  
	- PrimarySourceID: Foreign key to coreprimarysources > primarysourceid, if this doesn't exist then this row is junk and should be able to be deleted  
	- TrackID: Primary key  
	- ArtistID: Foreign key to coreartists > artistid, I wonder what happens if this doesn't exist? Probably breaks things horribly, because the artist name is in there  
	- AlbumID: Foreign key to corealbums > albumid  
	- TagSetID: ?  
	- MusicBrainzID: ?  
	- Uri: Location of the file as a file:// URI, e.g. "file:///home/megan/Music/some%20cool%20song.ogg"  
	- MimeType: Mime type of the file because that's clearly the cool way to identify a type, except it's not audio/whatever like you would think, and it's stuff like taglib/mp3 and taglib/ogg  
	- FileSize: File size in bytes (what happens when the file isn't found? Null? The last value from when it could be found?)  
	- BitRate: The bitrate, or if it's VBR then I guess it's like the average or whatever, it's the same as what displays in the Bit Rate column in the actual application  
	- SampleRate: Sample rate (natch)  
	- BitsPerSample: I've only ever seen 0 here, maybe it does something for some file type  
	- Attributes: ? Everything seems to be 5, my uneducated guess is that it's actually a bitfield  
	- LastStreamError: ? Seems to be 0 everywhere, maybe if a playback error occured this would be updated with an error code until you played it successfully?  
	- Title: Title of the song  
	- TitleLowered: Title in lowercase  
	- TitleSort: Version of title used for sorting, or Sort Title field in song properties  
	- TitleSortKey: blob  
	- TrackNumber: Track #, 0 if missing  
	- TrackCount: Total tracks (TrackNumber of x), 0 if missing  
	- Disc: Disc #, 0 if missing  
	- DiscCount: Total discs (Disc of x), 0 if missing  
	- Duration: Duration of the song in milliseconds  
	- Year: The year field, 0 if missing  
	- Genre: The genre field, always stored as a string even if it's an MP3 file with that stupid old ID3 tag format that stores it as numbers in the file  
	- Composer: The composer field if applicable  
	- Conductor: The conductor field if applicable  
	- Grouping: The grouping field if applicable  
	- Copyright: The copyright field if applicable  
	- LicenseURI: The license URI field if applicable (who uses that?)  
	- Comment: The comment field if applicable  
	- Rating: The star rating, stored as a number from 1 to 5, or 0 if you haven't given it a rating yet. None of those fractional ratings or numbers that scale up to 100 here  
	- Score: It's whatever that score field that you can view as a column in the thing does  
	- PlayCount: The play count, 0 if never played. Sometimes I've seen this get corrupted and it becomes some stupidly high number which is clearly wrong (like in the millions), I don't know why  
	- SkipCount: Oh crap it keeps track of how often you skip a song? Now I feel guilty every time I don't feel like listening to something  
	- LastPlayedStamp: Last played, stored as Unix timestamp  
	- LastSkippedStamp: Last skipped, stored as Unix timestamp  
	- DateAddedStamp: Date/time added to library, stored as Unix timestamp  
	- DateUpdatedStamp: Date/time last updated, stored as Unix timestamp  
	- MetadataHash: Some hexadecimal value different for each thing, I don't know what it does  
	- BPM: BPM or 0 if not entered  
	- LastSyncedStamp: Another Unix timestamp, I'm gonna guess that this is used for Banshee to know whether or not it should sync a song to a portable device, perhaps comparing to DateUpdatedStamp  
	- FileModifiedStamp: Also a Unix timestamp, I guess it's when the file itself is modified and not necessarily when something meaningful is updated which would update DateUpdatedStamp  

coverartdownloads  
Weh?? If I had to guess, it'd be involved in checking to see if Banshee's managed to download cover artwork for a certain album, and not downloading it again if it already has, but retrying later if it hasn't (without trying every 5 milliseconds and breaking the internet)  
	- AlbumID: Foreign key to corealbums > albumid I guess  
	- Downloaded: Seems to be 1 or 0?  
	- LastAttempt: Good ol' Unix timestamp  

hyenamodelversions  
Hyena is the name of Banshee's internal media management crap for lack of a better description, anyway, this looks like another key/value store. It all just has version numbers, so I'm not going to bother going into it too much, but you have:  
	- id: Well, it's the ID  
	- name: Key  
	- version: What you would call a value  

lastfmstations  
>using Last.fm in 2017  
>shiggy diggy  
Oh well for some reason I have some rows in here, though I never used last.fm for the radio stuff, probably because I'm in Australia so I couldn't  
	- StationID: Primary key I guess  
	- Creator: Hmm, I have "Zowayix" which would be my last.fm username in some rows, and empty string in the other, so I dunno
	- Name: I have stuff like "Recommended", "Banshee Group", "Neighbors" and "Creative Commons"  
	- Type: Stuff like "Recommended", "Personal", "Mix", "Group", "Tag"  
	- Arg: I see a "Zowayix" and a "Banshee" and a "creative commons" in there, if I had to guess it'd combine with Type to determine what the content of the station actually is and Name is just arbitrary  
	- PlayCount: All of these are 0 LEL  

lyricsdownloads  
I don't have any rows in here, so I'm not sure what it does. The columns are TrackID and Downloaded though, which I'd be willing to bet is a foreign key to coretracks > trackid and a boolean respectively  

metadataproblems  
This is used by the Tools > Fix Music Metadata... option.  
	- ProblemID: Primary key I guess  
	- ProblemType: Type of the problem, e.g. "dupe-artist" means that there's an artist in your library with a duplicate name except differing in case, and I'm not sure of the other possible values here  
	- TypeOrder: ?  
	- Generation: ? It's all 11  
	- Selected: ?  
	- SolutionValue: This'd be the proposed solution to resolve the duplicates, e.g. if you have duplicate artists BLAH and Blah this might be Blah, I'm not sure how it chooses which of the two  
	- SolutionOptions: The two duplicates where you can choose one to resolve the issue, separated by two seimicolons, e.g. "deadmau5;;Deadmau5"  
	- ObjectIds: Two numbers separated by comma, maybe these are foreign keys to coreartists > artistid?   
	- ObjectCount: Not sure, but maybe ObjectIds isn't always two numbers and this column specifies how many there are, because I always have 2 here   

miragetrackanalysis  
??? I don't even have any rows  
	- TrackID: Maybe foreign key to coretracks > trackid?  
	- ScmsData: ????  
	- Status: ????  

podcastenclosures  
I don't use podcasts, so I have no rows here and can't really tell what it does specifically  
	- ItemID: ?  
	- EnclosureID: ?  
	- LocalPath: ?  
	- Url: ?  
	- Keywords: ?  
	- Duration: ?  
	- FileSize: ?  
	- DownloadedAt: ?   
	- DownloadStatus: ?  

podcastitems  
Something else involving podcasts, I would imagine, still no rows  
	- FeedID: ?  
	- LicenseUri: ?  
	- ItemID: ?   
	- Author: ?  
	- Comments: ?  
	- Description: ?  
	- StrippedDescription: ?  
	- Guid: ?   
	- IsRead: ?  
	- Link: ? He's the protagonist of the Legend of Zelda games but that's not important right now  
	- Modified: ?  
	- PubDate: ?  
	- Title: ?  
	- Active: ?  

podcastsyndications  
Another podcasty thing that I don't have rows for  
	- last_auto_download: ?  
	- AutoDownload: ?  
	- DownloadStatus: ?  
	- IsSubscribed: ?  
	- FeedID: ?  
	- Title: ?  
	- Description: ?  
	- Url: ?  
	- Keywords: ?  
	- Category: ?  
	- Copyright: ?  
	- ImageUrl: ?  
	- UpdatePeriodMinutes: ?  
	- Language: ?  
	- LastDownloadError: ?  
	- LastDownloadTime: ?  
	- Link: ?  
	- MaxItemCount: ?  
	- PubDate: ?  
	- LastBuildDate: ?  
	- SyncSetting: ?  
