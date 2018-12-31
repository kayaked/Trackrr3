import json
import urllib.parse
from datetime import datetime
import dateutil.parser

import aiohttp
from .base import Album
from .base import Song
from .keys import Keys


class napsterAPI:
    SEARCH_BASE = "https://api.napster.com/v2.2/search"
    TRACK_BASE = "https://api.napster.com/v2.2/tracks/"
    ALBUM_LOOKUP_BASE = "https://api.napster.com/v2.2/albums/"


class NotFound(Exception):
    pass


# Constructs a params to request with the default settings
# Keeps it clean
def construct_param(type, search_term: str):
    if type == "track":
        params = {
            "catalog": "US",
            "limit": 1,
            "offset": 0,
            "per_type_limit": 1,
            "query": search_term,
            "rights": 2,
            "type": "track"
        }
        return params
    elif type == "album":
        params = {
            "catalog": "US",
            "limit": 1,
            "offset": 0,
            "per_type_limit": 1,
            "query": search_term,
            "rights": 2,
            "type": "album"
        }
        return params


# Idk if this is needed, but just in case
# To Do: Random Generate User Agent
def construct_header():
    headers = {
        'apikey': Keys.DEV_NAPSTERAPI
    }
    return headers


# http://direct.napster.com/imageserver/v2/albums/{album_id}/images/{size}.{extension}
def return_image(album_id):
    return "http://direct.napster.com/imageserver/v2/albums/{}/images/500x500.jpg".format(album_id)


async def return_album_info(session, album_id):
    async with session.get(napsterAPI.ALBUM_LOOKUP_BASE + album_id, headers=construct_header()) as resp:
        resp_json = await resp.json()

        try:
            album_selected = resp_json['albums'][0]
        except KeyError:
            raise NotFound

    async with session.get(napsterAPI.ALBUM_LOOKUP_BASE + album_id + '/tracks', headers=construct_header()) as resp_2:

        try:
            response = await resp_2.json()
            track_list = response['tracks']
        except KeyError:
            raise NotFound

        tracks = []
        for track in track_list:
            tracks.append(track['name'])

        album_release_date_raw = dateutil.parser.parse(album_selected['released'])

        data = {
            "AlbumURL": 'https://us.napster.com/artist/' + album_selected['shortcut'].split('/')[0] + '/album/' + album_selected['shortcut'].split('/')[-1],
            "AlbumReleaseDate": album_release_date_raw,
            "TrackList": tracks,
            "AlbumCoverArt": return_image(album_id),
            "AlbumArtist": album_selected.get('artistName', 'N/A'),
            "AlbumName": album_selected.get('name', 'Unknown')
        }
        return data

async def search_album(album_name):
    form = {}
    async with aiohttp.ClientSession() as session:
        async with session.get(napsterAPI.SEARCH_BASE, headers=construct_header(), params=construct_param("album", album_name)) as resp:
            resp_json = await resp.json()
            try:
                album_selected = resp_json['search']['data']['albums'][0]
            except KeyError:
                raise NotFound

            album_id = album_selected['id']
        album_lookup = await return_album_info(session, album_id)

        return NapsterAlbum(album_lookup)

async def search_song(song_name):
    form = {}
    async with aiohttp.ClientSession() as session:
        async with session.get(napsterAPI.SEARCH_BASE, headers=construct_header(), params=construct_param("track", song_name)) as resp:
            resp_json = await resp.json()
            try:
                track_selected = resp_json['search']['data']['tracks'][0]
            except KeyError:
                raise NotFound

            album_id = track_selected['albumId']
            try:
                form['TrackName'] = track_selected['name']
                form['TrackArtist'] = track_selected['artistName']
                form['TrackAlbum'] = track_selected['albumName']
            except KeyError:
                raise KeyError("Napster 116-120")

            album_lookup = await return_album_info(session=session, album_id=album_id)
            if album_lookup is None:
                raise NotFound

            else:
                pass

            try:
                shortcut = track_selected['shortcut'].split('/')
                form['TrackCoverArt'] = return_image(album_id)
                form['TrackReleaseDate'] = album_lookup['AlbumReleaseDate']
                form['TrackURL'] = 'https://us.napster.com/artist/' + shortcut[0] + '/album/' + shortcut[1] + '/track/' + shortcut[-1]
            except KeyError:
                raise KeyError('Napster 131-138')

            return NapsterSong(form)


class NapsterSong(Song):

    def __init__(self, data: dict):
        self.color = 0x586474
        self.service = 'Napster'
        self.name = data['TrackName']
        self.artist = data['TrackArtist']
        self.link = data['TrackURL']
        self.cover_url = data['TrackCoverArt']
        self.track_album = data['TrackAlbum']
        self.release_date = data['TrackReleaseDate']


class NapsterAlbum(Album):

    def __init__(self, data: dict):
        self.color = 0x586474
        self.service = 'Napster'
        self.name = data['AlbumName']
        self.artist = data['AlbumArtist']
        self.link = data['AlbumURL']
        self.cover_url = data['AlbumCoverArt']
        self.track_list = data['TrackList']
        self.release_date = data['AlbumReleaseDate']