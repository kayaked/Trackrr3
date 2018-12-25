import aiohttp
from .base import *
from datetime import datetime

class GeniusAPI:
    BASE = 'https://genius.com/api'
    # Ok so basically api.genius.com requires a key but this one does not??? IDK genius fix ur shit
    # A ton of their end-points aren't even documented so i might as well do somethin here

async def search_album(album_name):
    """ Searches an album by name on Genius. """

    async with aiohttp.ClientSession() as session:
        # Searches albums (example: https://genius.com/api/search/albums?q=ASTROWORLD)
        async with session.get(GeniusAPI.BASE + '/search/albums', params={'q': album_name}) as resp:
            resp_json = await resp.json()

        hits = resp_json.get('response', {}).get('sections', [])
        if not hits:
            raise NotFound
        hits = hits[0].get('hits')
        if not hits:
            raise NotFound
        hit = hits[0].get('result', {}).get('id', 0)

        # Example: https://genius.com/api/albums/34024
        async with session.get(GeniusAPI.BASE + f'/albums/{hit}') as resp:
            resp2_json = await resp.json()

        hits = resp2_json.get('response', {}).get('album', {})

        # Retrieves tracklist.
        # Example: https://genius.com/api/albums/34024/tracks
        async with session.get(GeniusAPI.BASE + f'/albums/{hit}/tracks') as resp:
            tl2_json = await resp.json()

        hits['track_list'] = [a.get('song', {}).get('title', '') for a in tl2_json.get('response', {}).get('tracks', [])]

        return GeniusAlbum(hits)

async def search_song(song_name):
    """ Searches an album by name on Genius. """

    async with aiohttp.ClientSession() as session:
        # Searches songs on Genius (example: https://genius.com/api/search/songs?q=Watch)
        async with session.get(GeniusAPI.BASE + '/search/songs', params={'q': song_name}) as resp:
            resp_json = await resp.json()

        hits = resp_json.get('response', {}).get('sections', [])
        if not hits:
            raise NotFound
        hits = hits[0].get('hits')
        if not hits:
            raise NotFound
        hit = hits[0].get('result', {}).get('id', 0)

        # Example: https://genius.com/api/songs/34024
        async with session.get(GeniusAPI.BASE + f'/songs/{hit}') as resp:
            resp2_json = await resp.json()

        hits = resp2_json.get('response', {}).get('song', {})

        return GeniusSong(hits)

class GeniusAlbum(Album):

    def __init__(self, data:dict):
        self.color = 0xffff00
        self.service = 'Genius'
        self.name = data.get('name', '')
        self.artist = data.get('artist', {}).get('name', 'N/A')
        self.link = data.get('url', 'https://genius.com/')
        self.track_list = data.get('track_list')
        self.cover_url = data.get('cover_art_url', 'https://github.com/exofeel/Trackrr/blob/master/assets/UnknownCoverArt.png?raw=true')
        self.release_date = datetime.strptime(data.get('release_date', '1970-01-01'), '%Y-%m-%d')

class GeniusSong(Song):

    def __init__(self, data:dict):
        self.color = 0xffff00
        self.service = 'Genius'
        self.name = data.get('title', 'N/A')
        self.artist = data.get('primary_artist', {}).get('name', 'N/A')
        self.link = data.get('url', 'https://genius.com/')
        self.track_album = ', '.join([album.get('name') for album in data.get('albums')]) if data.get('albums') else 'N/A'
        self.cover_url = data.get('song_art_image_url', 'https://github.com/exofeel/Trackrr/blob/master/assets/UnknownCoverArt.png?raw=true')
        self.release_date = datetime.strptime(data.get('release_date', '1970-01-01'), '%Y-%m-%d')