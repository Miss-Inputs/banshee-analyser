/* 
 * To change this license header, choose License Headers in Project Properties.
 * To change this template file, choose Tools | Templates
 * and open the template in the editor.
 */
/**
 * Author:  megan
 * Created: 16/04/2017
 */
--Unused currently, but it's here, it will probably not be in a big SQL file when used
--The sections that aren't the last two should be safe to run at any time
--Is albumartwriter just a cache? Can I clear that out any time I want? I think at some point
--I'll have to peek at Banshee's source code to tell exactly what it uses all these tables for


-- Get rid of anything belonging to sources that don't exist (e.g. USB devices from long ago)
DELETE FROM coretracks WHERE primarySourceID NOT IN (SELECT primarysourceid FROM coreprimarysources);
DELETE FROM coreplaylists WHERE primarySourceID NOT IN (SELECT primarysourceid FROM coreprimarysources);
DELETE FROM coresmartplaylists WHERE primarysourceid NOT IN (SELECT primarysourceid FROM coreprimarysources);
DELETE FROM coretracks WHERE primarysourceid NOT IN (SELECT primarysourceid FROM coreprimarysources);

-- Get rid of things related to tracks that don't exist
DELETE FROM bookmarks WHERE trackid NOT IN (SELECT trackid FROM coretracks)
DELETE FROM coreshufflemodifications WHERE trackid NOT IN (SELECT trackid FROM coretracks); --Could this table be truncated completely? What does it do
DELETE FROM coreplaylistentries WHERE trackid NOT IN (SELECT trackid FROM coretracks);
DELETE FROM coresmartplaylistentries WHERE trackid NOT IN (SELECT trackid FROM coretracks);
DELETE FROM lyricsdownloads WHERE trackid NOT IN (SELECT trackid FROM coretracks);
DELETE FROM coreshuffles WHERE trackid NOT IN (SELECT trackid FROM coretracks); --Could this table be truncated completely? What does it do

-- Get rid of crap that refers to albums that don't exist
DELETE FROM coverartdownloads WHERE albumid NOT IN (SELECT albumid FROM corealbums);
DELETE FROM albumartwriter WHERE albumid NOT IN (SELECT albumid FROM corealbums);

-- Get rid of entries for playlists that don't exist
DELETE FROM coreplaylistentries WHERE playlistid NOT IN (SELECT playlistid FROM coreplaylists);
DELETE FROM coresmartplaylistentries WHERE smartplaylistid NOT IN (SELECT smartplaylistid FROM coresmartplaylists);

--Maybe you want to truncate this table every now and then, I'm not sure. I can tell that it's
--telemetry data of course, and from looking at it, it has stuff like the last SQL command executed
--and other less interesting things. But how often does this get submitted to the Banshee
--developers (if it doesn't, what's the point of it)?
DELETE FROM anonymoususagedata;

--This will make Banshee forget about any portable device you ever plugged in, basically
--So maybe you don't want to do that, but it's here for reference
DELETE FROM coreprimarysources WHERE (StringID LIKE 'MassStorageSource%' OR StringID LIKE 'DaapSource%');
DELETE FROM corecachemodels WHERE (modelid LIKE 'MassStorageSource-%' OR modelid LIKE 'DaapSource-%');
