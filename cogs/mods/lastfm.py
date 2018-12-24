import aiohttp
from .base import Album
from datetime import datetime
import urllib.parse
from .keys import Keys

class lfmAPI:
    BASE = 'http://ws.audioscrobbler.com/2.0/'
    KEY = Keys.LASTFM

class NotFound(Exception):
    pass

async def _fetch(method, **kw):
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
    response = await _fetch('album.search', album=album_name)
    
    if 'error' in response:
        if response['error'] == 10:
            raise InvalidKey("Your last.fm API key is not valid.")
        raise NotFound(f"Unknown error code {response['error']}")
    
    results = response.get('results', {}).get('albummatches', {}).get('album', [])

    if not results:
        raise NotFound
    
    results=results[0]

    response = await _fetch('album.getinfo', album=results.get('name', ''), artist=results.get('artist', 'N/A'))
    response = response.get('album', {}).get('tracks', {}).get('track', [])
    results['track_list'] = [ tr.get('name', '') for tr in response ]

    return LFMAlbum(results)

class LFMAlbum(Album):

    def __init__(self, data:dict):
        self.color = 0x7c0000
        self.service = 'LastFM'
        self.name = data.get('name', '')
        self.artist = data.get('artist', 'N/A')
        self.link = data.get('url', 'https://genius.com/')
        self.track_list = data.get('track_list')
        self.cover_url = data.get('image', [])[-1].get('#text', 'https://cdn.shopify.com/s/files/1/2009/8293/products/ZM1650.jpg?v=1515009062')
        self.release_date = datetime.today()