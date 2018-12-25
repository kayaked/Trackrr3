import json
import urllib.parse
from datetime import datetime

import aiohttp

from .base import Album
from .base import Song


class itunesAPI:
    BASE = 'https://itunes.apple.com'

class NotFound(Exception):
    pass

# Constructs a link to request with the default settings
def construct_link(type, search_term:str):
    if type == "album":
        params = {
            "term": search_term,
            "entity": "album"
        }
        url = itunesAPI.BASE + "/search?" + urllib.parse.urlencode(params)
        return url
    elif type == "track":
        params = {
            "term": search_term,
            "entity": "song"
        }
        url = itunesAPI.BASE + "/search?" + urllib.parse.urlencode(params)
        return url

async def search_album(album_name):
    """ Searches an album by name on iTunes/AppleMusic. """
    async with aiohttp.ClientSession() as session:
        url = construct_link(type="album", search_term=album_name)
        #async with session.get(itunesAPI.BASE + '/search', params={'term': album_name, 'media': 'music', 'entity': 'album'}) as resp:
        async with session.get(url) as resp:
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


async def search_song(song_name):
    async with aiohttp.ClientSession() as session:
        url = construct_link(type="track", search_term=song_name)
        async with session.get(url) as resp:
            resp_json = await resp.json(content_type=None)
            result_count = resp_json['resultCount']
            if int(result_count) == 0:
                raise NotFound
            else:
                track_selected = resp_json['results'][0]

    

                async def release_date():
                    datetime_formatted = datetime.strptime(track_selected['releaseDate'], '%Y-%m-%dT%H:%M:%SZ')
                    return datetime_formatted
    

                form = {
                    "TrackName": track_selected['trackName'],
                    "TrackArtist": track_selected['artistName'],
                    "TrackURL": track_selected['trackViewUrl'],
                    "TrackCoverArt": track_selected['artworkUrl100'],
                    "TrackReleaseDate": await release_date(),
                    "TrackAlbum": track_selected['collectionName']
                }

                return iTunesSong(form)





class iTunesSong(Song):
    
    def __init__(self, data:dict):
        self.color = 0xe98def
        self.service = 'iTunes'
        self.name = data['TrackName']
        self.artist = data['TrackArtist']
        self.link = data['TrackURL']
        self.cover_url = data['TrackCoverArt']
        self.track_album = data['TrackAlbum']
        self.release_date = data['TrackReleaseDate']


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
