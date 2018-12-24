import aiohttp
from .base import *
from datetime import datetime
import urllib.parse
from .keys import Keys

# Tidal you are stoopid

class DeezerAPI:
    BASE = 'http://api.deezer.com'

async def search_album(album_name):
    params = {
        'q':album_name,
        'index':0,
        'limit':1,
        'output':'json'
    }
    async with aiohttp.ClientSession() as session:
        async with session.get(DeezerAPI.BASE + '/search/album/', params=params) as resp:
            response = await resp.json()
    
    results = response.get('data', [])

    if not results:
        raise NotFound
    
    results=results[0]

    async with aiohttp.ClientSession() as session:
        async with session.get(DeezerAPI.BASE + f'/album/{results.get("id", 0)}', params=params) as resp:
            response = await resp.json()
    responsetr = response.get('tracks', {}).get('data', [])
    results['track_list'] = [ tr.get('title', '') for tr in responsetr ]
    results['release_date'] = response.get('release_date', '1970-01-01')
    return DeezerAlbum(results)

class DeezerAlbum(Album):

    def __init__(self, data:dict):
        self.color = 0x222222
        self.service = 'Deezer'
        self.name = data.get('title', 'N/A')
        self.artist = [artist.get('name', '') for artist in data.get('contributors', [])] if data.get('contributors') else 'N/A'
        self.link = data.get('link', 'https://deezer.com/')
        self.track_list = data.get('track_list', [])
        self.cover_url = data.get('cover_xl') if data.get('cover_xl') else 'https://cdn.shopify.com/s/files/1/2009/8293/products/ZM1650.jpg?v=1515009062'
        self.release_date = datetime.strptime(data.get('release_date', '1970-01-01'), '%Y-%m-%d')