import aiohttp, bs4
from .base import *
from datetime import datetime

class PlayAPI:
    BASE = 'https://play.google.com'

async def search_album(album_name):
    """ Album searcher for the Google Play Music site. Does not use the API as of now """
    async with aiohttp.ClientSession() as session:
        params = {
            'q': album_name,
            'c': 'music'
        }
        # Gets the standard search HTML page.
        async with session.get(PlayAPI.BASE + '/store/search', params=params) as resp:
            resp_text = await resp.text()

    soup = bs4.BeautifulSoup(resp_text, 'html.parser')
    # Finds the results panel with Albums
    panels = [panel for panel in soup.find_all('div', {'class':'id-cluster-container cluster-container cards-transition-enabled'}) if 'Albums' in getattr(panel, 'text', '')]
    if not panels:
        return NotFound
    # Gets the first result
    panel = panels[0].find('div', {'class':'id-card-list card-list two-cards'})
    results = list(getattr(panel, 'children', []))
    if not results:
        return NotFound
    
    results = results[0]

    hits = {}

    hits['name'] = results.find('a', {'class':'title'}).text.strip()
    hits['link'] = PlayAPI.BASE + results.find('a', {'class':'card-click-target'}).get('href', '/store/')
    hits['artist'] = results.find('a', {'class':'subtitle'}).text.strip()
    hits['cover_url'] = results.find('img', {'class':'cover-image'}).get('src', 'https://github.com/exofeel/Trackrr/blob/master/assets/UnknownCoverArt.png?raw=true')

    # I run into this a lot, having to make another request for the fucking track list. Pleas just put it in the first 1 🙏
    async with aiohttp.ClientSession() as session:
        print(hits['link'])
        async with session.get(hits['link']) as resp:
            resp_text = await resp.text()

    soup = bs4.BeautifulSoup(resp_text, 'html.parser')
    track_list = soup.find('table', {'class':'track-list'}).find_all('tr', {'class':'track-list-row'})
    [print(tracc.find('div', {'class':'title'})) for tracc in track_list]
    hits['track_list'] = [tracc.find('div', {'class':'title'}).text.strip() for tracc in track_list]
    try:
        hits['release_date'] = [info for info in soup.find_all('div', {'class':'meta-info'}) if 'Released' in info.text][0].find('div', {'class':'content'}).text
    except:
        hits['release_date'] = 'January 1, 1970'

    return PlayAlbum(hits)

class PlayAlbum(Album):

    def __init__(self, data:dict):
        self.color = 0xeeeeee
        self.service = 'Play'
        self.name = data.get('name', 'N/A')
        self.artist = data.get('artist', 'N/A')
        self.link = data.get('link', 'https://play.google.com/')
        self.track_list = data.get('track_list', [])
        self.cover_url = data.get('cover_url')
        self.release_date = datetime.strptime(data.get('release_date', 'January 1, 1970'), '%B %d, %Y')