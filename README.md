# AMPINTRUDER

* uses python-mpv
* uses youtube-dl via the integrated python bindings
* caches downloaded titles locally
* caches playlists locally

## current state of affairs:

* uses html + css for ui rendering
* uses veritable POST-request handling instead of a web framework
* can't play song while it is downloading (does not use youtube-dl through mpv)
* uses threading to work download-queues independant of UI request handling
* song queue is stored in mpv only, dict ```seq_to_id``` is used to keep track of added items

## TODO

* better UI
* use youtube-dl through mpv (for instant play only ?)
* update playlists
* video support ?
