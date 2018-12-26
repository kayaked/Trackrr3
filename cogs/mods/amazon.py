import aiohttp
from .base import *
from datetime import datetime
import urllib.parse
from .keys import Keys
from .amazonkeys import AmazonKeys

# It's probably pretty confusing to look at this one LOL
# i've hidden pretty much all info about the request, just cause i'm not sure if it has any info about me. The payload is pretty damn big, def too big for this file
# But Gang stuff almost no one has done this yet 🤙

async def search_album(album_name):
    """ Amazon album searcher. """
    payload = AmazonKeys.PAYLOAD
    payload['query']['must'][0]['query'] = album_name
    async with aiohttp.ClientSession() as session:
        async with session.post(AmazonKeys.BASE + 'search/v1_1/', headers=AmazonKeys.HEADERS, json=payload, timeout=5) as resp:
            response = await resp.json()

    results = [result for result in response.get('results') if result.get('label', '') == 'catalog_albums']

    if not results:
        raise NotFound

    hits = results[0].get('hits', [])

    if not hits:
        raise NotFound

    hit = hits[0].get('document', {})

    payload = AmazonKeys.PAYLOAD_TRACK

    payload['asins'][0] = hit.get('asin', '')

    async with aiohttp.ClientSession() as session:
        async with session.post(AmazonKeys.BASE + 'muse/legacy/lookup', headers=AmazonKeys.HEADERS, json=payload) as resp:
            response = await resp.json()

    rlis = response.get('albumList', [])

    if not rlis:
        raise NotFound

    hit['track_list'] = [tracc.get('title', '') for tracc in rlis[0].get('tracks')]

    return AmazonAlbum(hit)

async def search_song(song_name):
    """ Amazon song searcher. """
    payload = AmazonKeys.PAYLOAD
    payload['query']['must'][0]['query'] = song_name
    async with aiohttp.ClientSession() as session:
        async with session.post(AmazonKeys.BASE + 'search/v1_1/', headers=AmazonKeys.HEADERS, json=payload, timeout=5) as resp:
            response = await resp.json()

    results = [result for result in response.get('results') if result.get('label', '') == 'catalog_tracks']

    if not results:
        raise NotFound

    hits = results[0].get('hits', [])

    if not hits:
        raise NotFound

    hit = hits[0].get('document', {})

    return AmazonSong(hit)

class AmazonAlbum(Album):

    def __init__(self, data:dict):
        self.color = 0x157FC3
        self.service = 'Amazon'
        self.name = data.get('title', 'N/A')
        self.artist = data.get('artistName', 'N/A')
        self.link = 'https://music.amazon.com/albums/' + data.get('asin', '') + '?tab=catalog'
        self.track_list = data.get('track_list', ['N/A'])
        self.cover_url = data.get('artFull', {}).get('URL', 'https://github.com/exofeel/Trackrr/blob/master/assets/UnknownCoverArt.png?raw=true').replace('500', '1024')
        self.release_date = datetime.fromtimestamp(data.get('originalReleaseDate', 18000))

class AmazonSong(Song):

    def __init__(self, data:dict):
        self.color = 0x157FC3
        self.service = 'Amazon'
        self.name = data.get('title', 'N/A')
        self.artist = data.get('artistName', 'N/A')
        self.link = 'https://music.amazon.com/tracks/' + data.get('asin', '') + '?tab=catalog'
        self.track_album = data.get('albumName', 'N/A')
        self.cover_url = data.get('artFull', {}).get('URL', 'https://github.com/exofeel/Trackrr/blob/master/assets/UnknownCoverArt.png?raw=true').replace('500', '1024')
        self.release_date = datetime.fromtimestamp(data.get('originalReleaseDate', 18000))