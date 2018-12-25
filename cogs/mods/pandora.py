import aiohttp
from .base import *
from datetime import datetime
import urllib.parse
from .keys import Keys

class PandoraAPI:
    BASE = 'https://www.pandora.com/api/v1/'

async def search_song(song_name):
    """ Album searcher by provided name on Pandora. """
    headers = Keys.PANDORAHEADERS
    payload = {'query': song_name, 'type': 'all', 'maxItemsPerCategory': 1}
    async with aiohttp.ClientSession() as session:
        async with session.post(PandoraAPI.BASE + 'search/fullSearch', headers=headers, json=payload) as resp:
            response = await resp.json()
    
    results = [i for i in response.get('items', []) if i.get('type') == 'track']

    if not results:
        raise NotFound
    
    results=results[0]

    rid = results.get('musicId', '')

    payload = {'token':rid}

    async with aiohttp.ClientSession() as session:
        async with session.post(PandoraAPI.BASE + f'music/track', json=payload, headers=headers) as resp:
            response = await resp.json()
    print(response)
    return PandoraSong(response)

class PandoraSong(Song):

    def __init__(self, data:dict):
        self.color = 0xffffff
        self.service = 'Pandora'
        self.name = data.get('songTitle', 'N/A')
        self.artist = data.get('artistName', 'N/A')
        self.link = data.get('trackDetailUrl', 'https://pandora.com/')
        self.cover_url = data.get('albumArt')[-1].get('url')
        self.track_album = data.get('albumTitle', 'N/A')
        self.release_date = datetime.strptime('1970-01-01', '%Y-%m-%d')