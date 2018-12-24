import aiohttp
from .base import Album
from datetime import datetime

class GeniusAPI:
    BASE = 'https://genius.com/api'

class NotFound(Exception):
    pass

async def search_album(album_name):

    async with aiohttp.ClientSession() as session:
        async with session.get(GeniusAPI.BASE + '/search/albums', params={'q': album_name}) as resp:
            resp_json = await resp.json()

        hits = resp_json.get('response', {}).get('sections', [])
        if not hits:
            raise NotFound
        hits = hits[0].get('hits')
        if not hits:
            raise NotFound
        hit = hits[0].get('result', {}).get('id', 0)

        async with session.get(GeniusAPI.BASE + f'/albums/{hit}') as resp:
            resp2_json = await resp.json()

        hits = resp2_json.get('response', {}).get('album', {})

        async with session.get(GeniusAPI.BASE + f'/albums/{hit}/tracks') as resp:
            tl2_json = await resp.json()

        hits['track_list'] = [a.get('song', {}).get('title', '') for a in tl2_json.get('response', {}).get('tracks', [])]

        return GeniusAlbum(hits)

class GeniusAlbum(Album):

    def __init__(self, data:dict):
        self.color = 0xffff00
        self.service = 'Genius'
        self.name = data.get('name', '')
        self.artist = data.get('artist', {}).get('name', 'N/A')
        self.link = data.get('url', 'https://genius.com/')
        self.track_list = data.get('track_list')
        self.cover_url = data.get('cover_art_url')
        self.release_date = datetime.strptime(data.get('release_date', '1970-01-01'), '%Y-%m-%d')