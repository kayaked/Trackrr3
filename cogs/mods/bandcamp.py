import json
import urllib.parse
from datetime import datetime
import bs4

import aiohttp

from .base import Album, Song, NotFound

async def search_album(album_name):
    """ Searches an Album on BandCamp. (beta) """
    async with aiohttp.ClientSession() as session:
        async with session.get('https://bandcamp.com/api/fuzzysearch/1/autocomplete?q=' + album_name) as resp:
            response = await resp.json()

        results = response.get('auto', {}).get('results', [])
        results = [res for res in results if res.get('type') == 'a']
        if not results:
            raise NotFound
        result = results[0]
        async with session.get(result.get('url', 'https://bandcamp.com/')) as resp:
            response = await resp.text()
        try:
            result['release_date'] = response.split('album_release_date: "')[-1].split('",')[0].split(':')[0]
        except:
            result['release_date'] = '01 Jan 1970 00'
        result['track_list'] = [getattr(aa.find('span'), 'text', '') for aa in bs4.BeautifulSoup(response, 'html.parser').find('table', {'class':'track_list'}).find_all('tr')]

    return BandcampAlbum(result)

async def search_song(album_name):
    """ Searches a song on BandCamp. (beta) """
    async with aiohttp.ClientSession() as session:
        async with session.get('https://bandcamp.com/api/fuzzysearch/1/autocomplete?q=' + album_name) as resp:
            response = await resp.json()

        results = response.get('auto', {}).get('results', [])
        results = [res for res in results if res.get('type') == 't']
        if not results:
            raise NotFound
        result = results[0]
        async with session.get(result.get('url', 'https://bandcamp.com/')) as resp:
            response = await resp.text()
        try:
            result['release_date'] = response.split('album_release_date: "')[-1].split('",')[0].split(':')[0]
        except:
            result['release_date'] = '01 Jan 1970 00'
        result['TrackAlbum'] = bs4.BeautifulSoup(response, 'html.parser').find('span', itemprop='inAlbum').text.strip()

    return BandcampSong(result)


class BandcampSong(Song):

    def __init__(self, data: dict):
        self.color = 0x408ea3
        self.service = 'Bandcamp'
        self.name = data.get('name', 'N/A')
        self.artist = data.get('band_name', 'N/A')
        self.link = data.get('url', 'https://bandcamp.com/')
        self.cover_url = data.get('img', 'https://github.com/exofeel/Trackrr/blob/master/assets/UnknownCoverArt.png?raw=true').replace('_3', '_16')
        self.track_album = data['TrackAlbum']
        self.release_date = datetime.strptime(data.get('release_date', '1970-01-01T00:00:00Z'), '%d %b %Y 00')


class BandcampAlbum(Album):

    def __init__(self, data: dict):
        self.color = 0x408ea3
        self.service = 'Bandcamp'
        self.name = data.get('name', 'N/A')
        self.artist = data.get('band_name', 'N/A')
        self.link = data.get('url', 'https://bandcamp.com/')
        self.track_list = data.get('track_list', [])
        self.cover_url = data.get('img', 'https://github.com/exofeel/Trackrr/blob/master/assets/UnknownCoverArt.png?raw=true').replace('_3', '_16')
        self.release_date = datetime.strptime(data.get('release_date', '1970-01-01T00:00:00Z'), '%d %b %Y 00')
