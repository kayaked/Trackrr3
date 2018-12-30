import aiohttp
from .base import *
from datetime import datetime
import urllib.parse
from .keys import Keys

class MusicBrainzAPI:
    BASE = 'https://musicbrainz.org/ws/2/'
    COVERBASE = 'http://coverartarchive.org/release/'

async def search_album(album_name):
    """ MusicBrainz album searcher. """
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
    results['cover'] = 'https://github.com/exofeel/Trackrr/blob/master/assets/UnknownCoverArt.png?raw=true'
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
        
        media = response.get('media', [])
        if not media:
            raise NotFound('no media;')
        trackraw = media[0].get('tracks', [])
        results['track_list'] = [ tr.get('title', '') for tr in trackraw ]
    
    # Gets release date
    release_date = response.get('date', '1970')
    if release_date.count('-') == 2:
        results['release_date'] = datetime.strptime(release_date, '%Y-%m-%d').strftime('%B %-d, %Y')
    elif release_date.count('-') == 1:
        results['release_date'] = datetime.strptime(release_date, '%Y-%m').strftime('%B %Y')
    elif release_date.count('-') == 0:
        results['release_date'] = release_date
    else:
        results['release_date'] = '1970'

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
        self.release_date = data.get('release_date')