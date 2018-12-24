import aiohttp
from .base import *
from datetime import datetime
import urllib.parse
from .keys import Keys

class MusicBrainzAPI:
    BASE = 'https://musicbrainz.org/ws/2/'
    COVERBASE = 'http://coverartarchive.org/release/'

async def search_album(album_name):
    params = {
        'query': album_name,
        'fmt': 'json'
    }
    async with aiohttp.ClientSession() as session:
        async with session.get(MusicBrainzAPI.BASE + 'release-group', params=params) as resp:
            response = await resp.json()
    
    if 'error' in response:
        raise NotFound(response['error'])
    
    results = response.get('release-groups', [])
    results = [result for result in results if result.get('primary-type', '') == 'Album']

    if not results:
        raise NotFound('no result')
    
    
    results=results[0]

    params.pop('query')
    params['inc'] = 'artist-credits+labels+discids+recordings'

    _id = results.get('releases', [])
    results['track_list'] = []
    results['cover'] = 'https://cdn.shopify.com/s/files/1/2009/8293/products/ZM1650.jpg?v=1515009062'
    if _id:
        image_resp = {}
        async with aiohttp.ClientSession() as session:
            for rel in _id:
                async with session.get(MusicBrainzAPI.COVERBASE + rel.get("id", "unknown")) as resp:
                    if resp.status != 200:
                        continue
                    try:
                        image_resp = await resp.json()
                    except:
                        continue
                    break

            async with session.get(MusicBrainzAPI.BASE + f'release/{_id[0].get("id", "unknown")}', params=params) as resp:
                response = await resp.json()

        if image_resp:
            image = image_resp.get('images', [])
            if image:
                results['cover']=image[0].get('image', '')
                async with aiohttp.ClientSession() as session:
                    async with session.get(results['cover'], allow_redirects=False) as resp:
                        download_url = resp.headers['location']
                    async with session.get(download_url, allow_redirects=False) as resp:
                        results['cover'] = resp.headers['location']
        
        if 'error' in response:
            raise NotFound(response['error'])
        
        response = response.get('media', [])
        if not response:
            raise NotFound('no media;')
        response = response[0].get('tracks', [])
        results['track_list'] = [ tr.get('title', '') for tr in response ]
    return MBAlbum(results)

class MBAlbum(Album):

    def __init__(self, data:dict):
        self.color = 0x963873
        self.service = 'MusicBrainz'
        self.name = data.get('title', 'N/A')
        self.artist = ', '.join([artist.get('artist', {}).get('name', '') for artist in data.get('artist-credit', [])]) if data.get('artist-credit') else 'N/A'
        self.link = data.get('url', 'https://musicbrainz.org/')
        self.track_list = data.get('track_list', [])
        self.cover_url = data.get('cover')
        self.release_date = datetime.strptime(data.get('date', '1970-01-01'), '%Y-%m-%d')