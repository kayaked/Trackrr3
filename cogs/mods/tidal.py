import aiohttp
from .base import Album
from datetime import datetime
import urllib.parse
from .keys import Keys

# Tidal you are stoopid

class TidalAPI:
    BASE = 'https://api.tidalhifi.com/v1/'
    KEY = Keys.TIDAL

class NotFound(Exception):
    pass

async def search_album(album_name):
    params = {
        'token': TidalAPI.KEY,
        'countryCode': 'US',
        'query': album_name,
        'limit': 1
    }
    async with aiohttp.ClientSession() as session:
        async with session.get(TidalAPI.BASE + 'search/albums', params=params) as resp:
            response = await resp.json()
    
    results = response.get('items', [])

    if not results:
        raise NotFound
    
    results=results[0]

    params['limit'] = 25

    async with aiohttp.ClientSession() as session:
        async with session.get(TidalAPI.BASE + f'albums/{results.get("id", 0)}/tracks', params=params) as resp:
            response = await resp.json()
    response = response.get('items', [])
    results['track_list'] = [ tr.get('title', '') for tr in response ]
    return TidalAlbum(results)

class TidalAlbum(Album):

    def __init__(self, data:dict):
        self.name = data.get('title', 'N/A')
        self.artist = data.get('artist', {}).get('name', 'N/A')
        self.link = data.get('url', 'https://genius.com/')
        self.track_list = data.get('track_list', [])
        self.cover_url = 'https://resources.tidal.com/images/' + data.get('cover').replace('-', '/') + '/1280x1280.jpg'
        print(self.cover_url)
        self.release_date = datetime.strptime(data.get('release_date', '1970-01-01'), '%Y-%m-%d')