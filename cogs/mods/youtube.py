##############################################################################################################
##############################################################################################################
import requests
from .ytmusickeys import YTMusicKeys
from .base import *
from datetime import datetime
import aiohttp
import copy

# Most of this module is not viewable atm. Sorry y'all

async def search_album(album_name):
    payload = YTMusicKeys.PAYLOAD
    payload['query'] = album_name
    payload['params'] = YTMusicKeys.ALBUM_PARAM_KEY
    async with aiohttp.ClientSession() as session:
        async with session.post(YTMusicKeys.URL + 'search', headers=YTMusicKeys.HEADERS, json=payload, params=YTMusicKeys.PARAMS) as resp:
            r = await resp.json()

    first_results = r['contents']['sectionListRenderer']['contents']

    if not first_results:
        raise NotFound

    index=0
    if not first_results[0].get('musicShelfRenderer'):
        first_results.pop(0)

    if not first_results:
        raise NotFound

    def thumbnail(res):
        return res['musicResponsiveListItemRenderer']['thumbnail']['musicThumbnailRenderer']['thumbnail']['thumbnails'][-1]['url']
    
    def textresults(res):
        return res['musicResponsiveListItemFlexColumnRenderer'].get('text', {}).get('runs', [{}])[0].get('text', '')

    def getId(res):
        return res.get('musicResponsiveListItemRenderer', {}).get('navigationEndpoint', {}).get('musicEntityBrowseEndpoint', {}).get('entityId', {}).get('musicAlbumReleaseEntity', 'https://music.youtube.com/')
    
    first_results = first_results[index].get('musicShelfRenderer', {}).get('contents', [])

    results = [[textresults(i) for i in a['musicResponsiveListItemRenderer']['flexColumns']] + [thumbnail(a), getId(a)] for a in first_results]

    if not results:
        raise NotFound
    results = results[0]

    result = {
        'name':results[0],
        'artist':results[2],
        'release_date':results[3],
        'cover_url':results[4],
        'id': results[5]
    }

    payload.pop('query')
    payload.pop('params')
    payload['entityId'] = {'musicAlbumReleaseEntity': result['id']}
    payload['pageId'] = 'DETAIL'
    
    async with aiohttp.ClientSession() as session:
        async with session.post(YTMusicKeys.URL + 'music/entity_browse', headers=YTMusicKeys.HEADERS, json=payload, params=YTMusicKeys.PARAMS) as resp:
            r = await resp.json()
    
    tracks = [pl for pl in r.get('payload', {}).get('payloads', []) if pl.get('track')]

    if tracks:
        result['track_list'] = [track.get('track', {}).get('title', '') for track in tracks]

    return YTMusicAlbum(result)

async def search_song(song_name):
    payload = YTMusicKeys.PAYLOAD
    payload['query'] = song_name
    payload['params'] = YTMusicKeys.SONG_PARAM_KEY
    async with aiohttp.ClientSession() as session:
        async with session.post(YTMusicKeys.URL + 'search', headers=YTMusicKeys.HEADERS, json=payload, params=YTMusicKeys.PARAMS) as resp:
            r = await resp.json()
    first_results = r['contents']['sectionListRenderer']['contents']

    if not first_results:
        raise NotFound

    index=0
    if not first_results[0].get('musicShelfRenderer'):
        first_results.pop(0)

    if not first_results:
        raise NotFound

    def thumbnail(res):
        return res['musicResponsiveListItemRenderer']['thumbnail']['musicThumbnailRenderer']['thumbnail']['thumbnails'][-1]['url']
    
    def textresults(res):
        return res['musicResponsiveListItemFlexColumnRenderer'].get('text', {}).get('runs', [{}])[0].get('text', '')

    def getId(res):
        return res.get('musicResponsiveListItemRenderer', {}).get('doubleTapCommand', {}).get('watchEndpoint', {}).get('videoId', '')
    
    first_results = first_results[index].get('musicShelfRenderer', {}).get('contents', [])

    results = [[textresults(i) for i in a['musicResponsiveListItemRenderer']['flexColumns']] + [thumbnail(a), getId(a)] for a in first_results]

    if not results:
        raise NotFound
    results = results[0]

    result = {
        'name':results[0],
        'artist':results[1],
        'track_album':results[2],
        'release_date':results[3],
        'cover_url':results[4],
        'id':results[5]
    }

    return YTMusicSong(result)

class YTMusicSong(Song):

    def __init__(self, data:dict):
        self.color = 0xff0000
        self.service = 'YouTube'
        self.name = data['name']
        self.artist = data['artist']
        self.link = 'https://youtube.com/watch?v=' + data.get('id', '')
        self.track_album = data['track_album']
        self.cover_url = data['cover_url']
        self.release_date = datetime(1970, 1, 1)

class YTMusicAlbum(Album):

    def __init__(self, data:dict):
        self.color = 0xff0000
        self.service = 'YouTube'
        self.name = data['name']
        self.artist = data['artist']
        self.link = 'https://music.youtube.com/album/' + data.get('id', '')
        self.track_list = data.get('track_list', ['N/A'])
        self.cover_url = data['cover_url']
        self.release_date = datetime.strptime(data['release_date'], '%Y')
##############################################################################################################
##############################################################################################################

# Coming soon