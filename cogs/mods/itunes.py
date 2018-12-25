import aiohttp
from .base import *
from datetime import datetime
import urllib.parse
import json

class itunesAPI:
    BASE = 'https://itunes.apple.com'

async def search_album(album_name):
    """ Searches an album by name on iTunes/AppleMusic. """
    async with aiohttp.ClientSession() as session:
        async with session.get(itunesAPI.BASE + '/search', params={'term': album_name, 'media': 'music', 'entity': 'album'}) as resp:
            resp_json = await resp.text()
            resp_json = json.loads(resp_json.strip())
        resp_json = resp_json.get('results', [])
        if not resp_json:
            raise NotFound
        form = resp_json[0]
        # Looks at the song by ID to fetch track list
        async with session.get(f"{itunesAPI.BASE}/lookup?id={form['collectionId']}&entity=song") as resp:
            tracklist_resp = await resp.text()
            tracklist_resp = json.loads(tracklist_resp.strip())
            tracklist_resp = tracklist_resp.get('results', [])
        form['track_list'] = tracklist = [i.get('trackName', '') for i in tracklist_resp if i.get('wrapperType', '')=="track"]
    return iTunesAlbum(form)

class iTunesAlbum(Album):

    def __init__(self, data:dict):
        self.color = 0xe98def
        self.service = 'iTunes'
        self.name = data.get('collectionName', '')
        self.artist = data.get('artistName', 'N/A')
        self.link = data.get('collectionViewUrl', 'https://genius.com/')
        self.track_list = data.get('track_list')
        self.cover_url = data.get('artworkUrl100', 'https://github.com/exofeel/Trackrr/blob/master/assets/UnknownCoverArt.png?raw=true').replace('100x100', '400x400')
        self.release_date = datetime.strptime(data.get('releaseDate', '1970-01-01T00:00:00Z'), "%Y-%m-%dT%H:%M:%SZ")