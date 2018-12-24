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
        async with session.get(results.get('url', '') + '/player', params=SpinrillaAPI.AUTH) as resp:
            response = await resp.text()
            results['track_list'] = [tracc.get('data-title', '') for tracc in bs4.BeautifulSoup(response, 'html.parser').find('ol', {'class':'track-list'}).find_all('li')]
    return SpinrillaAlbum(results)

class SpinrillaAlbum(Album):

    def __init__(self, data:dict):
        self.color = 0x460856
        self.service = 'Spinrilla'
        self.name = data.get('title', 'N/A')
        self.artist = ', '.join([artist['display_name'] for artist in data.get('artist', [])])
        self.link = data.get('url', 'http://spinrilla.com/')
        self.track_list = data.get('track_list', [])
        self.cover_url = data.get('cover', {}).get('large', '')
        self.release_date = datetime.fromtimestamp(data.get('released_at', 18000))