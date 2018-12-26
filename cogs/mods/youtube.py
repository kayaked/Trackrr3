##############################################################################################################
##############################################################################################################
import requests
from .ytmusickeys import YTMusicKeys
from .base import *
from datetime import datetime
import aiohttp

async def search_album(album_name):
    payload = YTMusicKeys.PAYLOAD
    payload['query'] = album_name
    async with aiohttp.ClientSession() as session:
        async with session.post(YTMusicKeys.URL, headers=YTMusicKeys.HEADERS, json=payload, params=YTMusicKeys.PARAMS) as resp:
            r = await resp.json()
    first_results = r['contents']['sectionListRenderer']['contents'][0]['musicShelfRenderer']['contents'][0]['musicResponsiveListItemRenderer']

    results = [i['musicResponsiveListItemFlexColumnRenderer']['text']['runs'][0]['text'] for i in first_results['flexColumns']] + [first_results['thumbnail']['musicThumbnailRenderer']['thumbnail']['thumbnails'][-1]['url']]

    result = {
        'name':results[0],
        'artist':results[2],
        'release_date':results[3],
        'cover_url':results[4]
    }

    return YTMusicAlbum(result)

class YTMusicAlbum(Album):

    def __init__(self, data:dict):
        self.color = 0xff0000
        self.service = 'YouTube'
        self.name = data['name']
        self.artist = data['artist']
        self.link = 'https://youtube.com/'
        self.track_list = ['Unsupported (Wait for the rewrite of YTMusic module?)']
        self.cover_url = data['cover_url']
        self.release_date = datetime.strptime(data['release_date'], '%Y')
##############################################################################################################
##############################################################################################################

# Coming soon