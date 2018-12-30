import aiohttp
from .base import *
from datetime import datetime
import urllib.parse
from .keys import Keys
import json
import bs4

class SpinrillaAPI:
    BASE = Keys.SPINRILLA_BASE
    AUTH = Keys.SPINRILLA_KEY_ID_AGENT

async def search_album(album_name):
    """ Searches album info on Spinrilla. API base is not public as of now.
    
    Not sure if it's a good idea to provide a params example, so I'm not gonna for now.
    
    """
    payload = json.dumps({
        'params':urllib.parse.urlencode({
            'query':album_name,
            'hitsPerPage':'1'
        })
    })
    async with aiohttp.ClientSession() as session:
        async with session.post(SpinrillaAPI.BASE + 'indexes/Album_production/query', params=SpinrillaAPI.AUTH, data=payload) as resp:
            response = await resp.json()
    
    results = response.get('hits', [])

    if not results:
        raise NotFound
    
    results=results[0]

    async with aiohttp.ClientSession() as session:
        # Example: https://www.spinrilla.com/mixtapes/lil-peep-hellboy/player
        async with session.get(results.get('url', '') + '/player', params=SpinrillaAPI.AUTH) as resp:
            response = await resp.text()
            results['track_list'] = [tracc.get('data-title', '') for tracc in bs4.BeautifulSoup(response, 'html.parser').find('ol', {'class':'track-list'}).find_all('li')]
    return SpinrillaAlbum(results)

async def search_song(song_name):
    """ Searches song/track info on Spinrilla.
    This is not used anywhere on Spinrilla and AFAIK is only available here (aside from Spinrilla fullsearch ofcourse)
    """
    payload = json.dumps({
        'params':urllib.parse.urlencode({
            'query':song_name,
            'hitsPerPage':'1'
        })
    })
    async with aiohttp.ClientSession() as session:
        async with session.post(SpinrillaAPI.BASE + 'indexes/Track_production/query', params=SpinrillaAPI.AUTH, data=payload) as resp:
            response = await resp.json()
    
    results = response.get('hits', [])

    if not results:
        raise NotFound
    
    results=results[0]
    return SpinrillaSong(results)

class SpinrillaAlbum(Album):

    def __init__(self, data:dict):
        self.color = 0x460856
        self.service = 'Spinrilla'
        self.name = data.get('title', 'N/A')
        self.artist = ', '.join([artist['display_name'] for artist in data.get('artist', [])])
        self.link = data.get('url', 'http://spinrilla.com/')
        self.track_list = data.get('track_list', [])
        self.cover_url = data.get('cover', {}).get('large', 'https://github.com/exofeel/Trackrr/blob/master/assets/UnknownCoverArt.png?raw=true')
        self.release_date = datetime.fromtimestamp(data.get('released_at')) if data.get('released_at') is not None else 'Unknown'

class SpinrillaSong(Song):

    def __init__(self, data:dict):
        self.color = 0x460856
        self.service = 'Spinrilla'
        self.name = data.get('title', 'N/A')
        self.artist = str(data.get('artist', ''))
        self.link = data.get('url', 'http://spinrilla.com/')
        self.cover_url = data.get('cover', {}).get('large', 'https://github.com/exofeel/Trackrr/blob/master/assets/UnknownCoverArt.png?raw=true')
        self.track_album = data.get('album', {}).get('title', 'N/A') if data.get('album') else 'N/A'
        # Spinrilla does not provide the release date of their tracks anywhere onsite AFAIK, just albums.
        self.release_date = datetime.fromtimestamp(data.get('released_at')) if data.get('released_at') is not None else 'Unknown'