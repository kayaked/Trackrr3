import json
import urllib.parse
from datetime import datetime

import aiohttp
import bs4
import discord
import lxml

from .base import Album, NotFound
from .base import Song


class itunesAPI:
    BASE = 'https://itunes.apple.com'

# Constructs a link to request with the default settings
def construct_link(type, search_term:str):
    params={}
    if type == "album":
        params = {
            "term": search_term,
            "entity": "album"
        }
    elif type == "track":
        params = {
            "term": search_term,
            "entity": "song"
        }
    elif type == 'artist':
        params = {
            'term': search_term,
            'entity': 'musicArtist'
        }
    url = itunesAPI.BASE + "/search?" + urllib.parse.urlencode(params)
    return url

async def search_artist(artist):
    async with aiohttp.ClientSession() as session:
        url = construct_link(type='artist', search_term=artist)
        async with session.get(url) as resp:
            resp_json = await resp.json(content_type=None)

        artist_info = {
            'name':'Unknown Artist',
            'description':'No info.',
            'date_birth':'Unknown',
            'latest_release':'N/A',
            'home_town':'Somewhere, Earth',
            'image_url':'https://raw.githubusercontent.com/exofeel/Trackrr/master/assets/UnknownArtist.png',
            'genre':'All'
        }
        
        results = resp_json.get('results', [])

        if not results:
            raise NotFound

        
        top_result = results[0]
        
        # Get the URL from iTunes with info
        result_url = top_result.get('artistLinkUrl', 'https://itunes.apple.com/')

        # Request new URL
        async with session.get(result_url) as resp:
            artist_info_text = await resp.text()

        # Parse HTML with BeautifulSoup4
        soup = bs4.BeautifulSoup(artist_info_text, 'lxml')
        soup_json = json.loads(getattr(soup.find('script', type='application/ld+json'), 'text', '{}'))

        # Get name
        artist_info['name'] = soup_json.get('name', 'Unknown Artist')

        # Get desc.
        if 'description' in soup_json:
            artist_info['description'] = soup_json.get('description')
            if artist_info['description'].__len__() > 500:
                artist_info['description'] = artist_info['description'][:500] + f'[...]({result_url})'
        
        # Get Birth date, Genre and Home-town
        # cont == The containers on the page, such as DOB
        #find_cont = lambda cont: cont.find('dt', {'class':'we-truncate we-truncate--single-line ember-view we-about-artist-inline__details-label'})
        containers_raw = soup.find_all('div', {'class':'we-about-artist-inline__details-item'})
        born_containers = [cont for cont in containers_raw if 'BORN' in getattr(cont, 'text', '')]
        if born_containers:
            artist_info['date_birth'] = getattr(born_containers[0].find('dd'), 'text', 'Unknown').strip()
        home_town_containers = [cont for cont in containers_raw if 'HOMETOWN' in getattr(cont, 'text', '')]
        if home_town_containers:
            artist_info['home_town'] = getattr(home_town_containers[0].find('dd'), 'text', 'Unknown').strip()
        genre_containers = [cont for cont in containers_raw if 'GENRE' in getattr(cont, 'text', '')]
        if genre_containers:
            artist_info['genre'] = getattr(genre_containers[0].find('dd'), 'text', 'Unknown').strip()
        
        # Get Latest Release info. /name
        latest_release_raw = soup.find("span", {"class": "featured-album__text__headline targeted-link__target"})
        latest_release = getattr(latest_release_raw, 'text', 'IDK')
        artist_info['latest_release'] = latest_release
        
        # Get artist picture
        found_image = soup.find("source", {"class" : "we-artwork__source"})
        if found_image:
            if found_image.get('srcset'):
                artist_info['image_url'] = found_image.get('srcset').split(',')[0].split(' ')[0]
        
        embed = discord.Embed(title=artist_info['name'] + ' <:itunes:526554505626779659>', url=result_url, timestamp=datetime.now(), color=discord.Color(0xe98def))
        embed.set_image(url=artist_info['image_url'])
        embed.add_field(name='Latest Release 🎵', value=artist_info['latest_release'])
        embed.add_field(name='Date of Birth 📆', value=artist_info['date_birth'])
        embed.add_field(name='Hometown 📌', value=artist_info['home_town'])
        embed.add_field(name='Genre 🎤', value=artist_info['genre'])
        embed.add_field(name=f'About {artist_info["name"]} 🗒', value=artist_info['description'])

        return embed
        

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
