import aiohttp
from .base import *
from datetime import datetime
import urllib.parse
import bs4
import re

# Tidal you are stoopid

class MonkeyAPI:
    BASE = 'https://mixtapemonkey.com'

async def search_album(album_name):
    params = {
        'name': album_name
    }
    async with aiohttp.ClientSession() as session:
        async with session.post(MonkeyAPI.BASE + '/mixtapes.inc.php', data=params) as resp:
            response = await resp.text()

    if not response:
        raise NotFound
    
    soup = bs4.BeautifulSoup(response, 'html.parser')

    result = [a for a in soup.find_all('a') if '/artist/' not in a['href']]

    if not result:
        raise NotFound

    result=result[0]

    hits = {}

    hits['title'] = result.find('span').text
    hits['artist'] = result.find('div', {'class':'searchtype-item-artist'}).text
    hits['link'] = MonkeyAPI.BASE + result['href']
    hits['cover_url'] = MonkeyAPI.BASE + result.find('img')['src']

    async with aiohttp.ClientSession() as session:
        async with session.get(MonkeyAPI.BASE + result['href']) as resp:
            response = await resp.text()
    soup = bs4.BeautifulSoup(response, 'html.parser')
    hits['track_list'] = [li['data-title'].strip() for li in soup.find('div', {'class':'player'}).find('ul').find_all('li')] # data-url attrs are DL links
    hits['release_date'] = getattr(soup.find('p', text=re.compile('Released')), 'text', 'Released in 1970').strip().split(' ')[-1]
    return MonkeyAlbum(hits)

class MonkeyAlbum(Album):

    def __init__(self, data:dict):
        self.color = 0xF24C1A
        self.service = 'MixtapeMonkey'
        self.name = data.get('title', 'N/A')
        self.artist = data.get('artist', 'N/A')
        self.link = data.get('link', 'https://mixtapemonkey.com/')
        self.track_list = data.get('track_list', [])
        self.cover_url = data.get('cover_url', 'https://github.com/exofeel/Trackrr/blob/master/assets/UnknownCoverArt.png?raw=true').replace('_thumb', '')
        self.release_date = datetime.strptime(data.get('release_date', '1970'), '%Y')