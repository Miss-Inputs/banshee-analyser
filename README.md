# banshee-analyser
This provides various information about a Banshee database that may be interesting/useful, e.g. playlists that contain the same track more than once, songs that have the same name as others, top 5 albums by average rating, or metadata problems such as tracks on the same album having the same disc & track number or fields being missing.

Ignore cli.py for now, it's a work in progress and by that I mean I haven't really started it. To use this, you'll have to either use core.py directly and call the function you want, or select a few things from a crappy menu in bansheeanalyser.py.

You'll also need python-dbus, PyGObject, and python-inflect (the latter being because I got carried away with the duplicate name detection, should probably be an optional dependency).