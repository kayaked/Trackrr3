import aiohttp
from .base import *
from datetime import datetime
import urllib.parse
from .keys import Keys

class lfmAPI:
    BASE = 'http://ws.audioscrobbler.com/2.0/'
    KEY = Keys.LASTFM

async def _fetch(method, **kw):
    """ Taken from Yak(oganessium)'s un-finished Last.FM module """
    params = {**kw, 'method':method, 'format':'json', 'api_key':lfmAPI.KEY}
    async with aiohttp.ClientSession() as session:
        async with session.get(lfmAPI.BASE + "?" + urllib.parse.urlencode(params).replace('+', '%20')) as apir:
            response = await apir.json()
    
    if 'error' in response:
        if response['error'] == 10:
            raise NotFound("Your last.fm API key is not valid.")
        raise ClientError(f"Unknown error code {response['error']}")

    return response

async def search_album(album_name):
    """ Searches an album by name on Last.FM. """
    response = await _fetch('album.search', album=album_name)
    if 'error' in response:
        if response['error'] == 10:
            raise NotFound("Your last.fm API key is not valid.") # https://www.last.fm/api/account/create
        raise NotFound(f"Unknown error code {response['error']}")
    
    results = response.get('results', {}).get('albummatches', {}).get('album', [])

    if not results:
        raise NotFound
    
    results=results[0] # Gets first result

    # Fetches track list from the extra album info End-point.
    response = await _fetch('album.getinfo', album=results.get('name', ''), artist=results.get('artist', 'N/A'))
    response = response.get('album', {}).get('tracks', {}).get('track', [])
    if not response:
        results['track_list'] = []
    else:
        results['track_list'] = [ tr.get('name', '') for tr in response ]

    return LFMAlbum(results)

async def search_song(song_name):
    """ Searches a song by name on Last.FM. """
    response = await _fetch('track.search', track=song_name)
    
    if 'error' in response:
        if response['error'] == 10:
            raise InvalidKey("Your last.fm API key is not valid.") # https://www.last.fm/api/account/create
        raise NotFound(f"Unknown error code {response['error']}")
    
    results = response.get('results', {}).get('trackmatches', {}).get('track', [])

    if not results:
        raise NotFound
    
    results=results[0] # Gets first result

    # Fetches album/cover from the extra song info End-point.
    response = await _fetch('track.getinfo', track=results.get('name', ''), artist=results.get('artist', 'N/A'))
    results['cover_url'] = response.get('track', {}).get('album', {}).get('image', [])
    if results['cover_url']:
        results['cover_url'] = results['cover_url'][-1].get('#text', 'https://github.com/exofeel/Trackrr/blob/master/assets/UnknownCoverArt.png?raw=true')
    else:
        results['cover_url'] = 'https://github.com/exofeel/Trackrr/blob/master/assets/UnknownCoverArt.png?raw=true'
    results['track_album'] = response.get('track', {}).get('album', {}).get('title', 'N/A')

    return LFMSong(results)

class LFMAlbum(Album):

    def __init__(self, data:dict):
        self.color = 0x7c0000
        self.service = 'LastFM'
        self.name = data.get('name', '')
        self.artist = data.get('artist', 'N/A')
        self.link = data.get('url', 'https://last.fm/')
        self.track_list = data.get('track_list')
        self.cover_url = data.get('image', [])[-1].get('#text', 'https://github.com/exofeel/Trackrr/blob/master/assets/UnknownCoverArt.png?raw=true')
        self.release_date = 'Unknown'

class LFMSong(Song):

    def __init__(self, data:dict):
        self.color = 0x7c0000
        self.service = 'LastFM'
        self.name = data.get('name', '')
        self.artist = data.get('artist', 'N/A')
        self.link = data.get('url', 'https://last.fm/')
        self.track_album = data.get('track_album')
        self.cover_url = data.get('cover_url')
        self.release_date = 'Unknown'