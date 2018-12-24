import aiohttp
from .base import *
from datetime import datetime
from .keys import Keys

class SoundCloudAPI:
    BASE = 'https://api-v2.soundcloud.com'
    TOKEN = Keys.SOUNDCLOUD

async def search_album(album_name):
    async with aiohttp.ClientSession() as session:
        if album_name.startswith("id:") and album_name[3:].strip().isdigit():
            params = {'client_id':SoundCloudAPI.TOKEN,'limit':'20'}
            async with session.get(f"https://api-v2.soundcloud.com/playlists/{album_name[3:].strip()}", params=params) as resp:
                try:
                    form = await resp.json()
                except IndexError:
                    raise NotFound
            return SoundCloudAlbum(form)
        else:
            params = {'client_id':SoundCloudAPI.TOKEN,'q':album_name,'limit':'20'}
            async with session.get(f"https://api-v2.soundcloud.com/search/albums", params=params) as resp:
                try:
                    form=await resp.json()
                    form=form['collection'][0]
                except IndexError:
                    raise NotFound
            async with session.get(form['uri'], params=params) as resp:
                track_list = await resp.json()
                form['track_list'] = [track.get('title', '') for track in track_list.get('tracks', [])]
                form['track_list_raw'] = track_list.get('tracks', [])

            return SoundCloudAlbum(form)

class SoundCloudAlbum(Album):

    def __init__(self, data:dict):
        self.color = 0xe08600
        self.service = 'SoundCloud'
        self.name = data.get('title', '')
        self.artist = data.get('user', {}).get('username', 'N/A')
        self.link = data.get('permalink_url', 'https://soundcloud.com/')
        self.track_list = data.get('track_list')
        self.cover_url = data.get('artwork_url').replace('large', 't500x500') if data.get('artwork_url') != None else data.get('track_list_raw', [])[0].get('artwork_url', 'https://cdn.shopify.com/s/files/1/2009/8293/products/ZM1650.jpg?v=1515009062').replace('large', 't500x500') if data.get('tracks') else ""
        self.release_date = datetime.strptime(data.get('created_at', '1970-01-01T00:00:00Z'), "%Y-%m-%dT%H:%M:%SZ")