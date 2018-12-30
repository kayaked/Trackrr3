from pyfy import AsyncSpotify, ClientCreds
#from .keys import SPOTIFYSECRET, SPOTIFYCLIENT, SPOTIFYSCOPE, SPOTIFYNAME, SPOTIFYREDIRECTURL
#from .base import Album
from .base import *
from .base import NotFound
from .keys import Keys
from datetime import datetime


# Ported from TrackrrV1-V2
# Now using PyFy async lib

class SpotifyError(Exception):
    pass

async def authorize_spotify():
    """ Authoirzies Spotify using PyFy's Method """
    client = ClientCreds(client_id=Keys.SPOTIFYCLIENT, client_secret=Keys.SPOTIFYSECRET)
    spotify = AsyncSpotify(client_creds=client)
    await spotify.authorize_client_creds()
    return spotify


async def search_song(song_name):
    """ Searches a track by name on the official Spotify API using PyFy."""
    spotify = await authorize_spotify()
    try:
        spotify_search_query = await spotify.search(song_name, types='track')
        track_selected = spotify_search_query['tracks']['items'][0]
    except IndexError:
        raise NotFound("No Results found for spotify")
    except Exception:
        raise NotFound("Error!")
    
    async def track_artist():
        try:
            return track_selected['artists'][0]['name']
        except IndexError:
            raise NotFound("No results for spotify")
        except Exception as err:
            print(err)
            return "Unknown!"

    async def track_name():
        try:
            return track_selected['name']
        except IndexError:
            raise NotFound("No results for spotify")
        except Exception as err:
            print(err)
            return "Unknown!"
    
    async def get_url():
        try:
            return track_selected['external_urls']['spotify']
        except IndexError:
            raise NotFound("No results for spotify")
        except Exception as err:
            print(err)
            return "Unknown!"

    async def get_cover_art():
        try:
            return track_selected['album']['images'][0]['url']
        except IndexError:
            raise NotFound("No results for spotify")
        except Exception as err:
            print(err)
            return "Unknown!"
    
    async def track_album():
        try:
            return track_selected['album']['name']
        except IndexError:
            raise NotFound("No results for spotify")
        except Exception as err:
            print(err)
            return "Unknown!"
   
    # The date the album was first released, for example “1981-12-15”. 
    # Depending on the precision, it might be shown as “1981” or “1981-12”.
    # The precision with which release_date value is known: “year” , “month” , or “day”.	
    async def get_release_date():
        album_selected = track_selected['album']
        album_release_date = album_selected['release_date']
        album_release_date_type = album_selected['release_date_precision']
        try:
            if album_release_date_type == "day":
               parsed_time = datetime.strptime(album_release_date, "%Y-%m-%d").strftime('%B %-d, %Y')
               return parsed_time
            elif album_release_date_type == "month":
                parsed_time = datetime.strptime(album_release_date, "%Y-%m").strftime('%B %Y')
                return parsed_time
            elif album_release_date_type == "year":
                return album_release_date
        except Exception:
            return datetime(1970, 1, 1)

    info = {
        "TrackName": await track_name(),
        "TrackArtist": await track_artist(),
        "TrackCoverArt": await get_cover_art(),
        "TrackAlbum": await track_album(),
        "TrackReleaseDate": await get_release_date(),
        "TrackURL": await get_url()
    }

    return SpotifySong(info)


async def search_album(album_name):
    """ Searches/finds an album by name on Spotify using PyFy. """
    spotify = await authorize_spotify()
    try:
        spotify_album_query = await spotify.search(album_name, types="album")
        album_selected = spotify_album_query['albums']['items'][0]       
    except IndexError:
        raise NotFound
    except Exception as error:
        return error

    async def get_album_name():
        try:
            return album_selected['name']
        except IndexError:
            raise NotFound
        except Exception as error:
            return error
    async def get_url():
        try:
            return album_selected['external_urls']['spotify']
        except IndexError:
            raise NotFound
        except Exception as error:
            return error
    
    async def get_cover_art():
        try:
            return album_selected['images'][0]['url']
        except IndexError:
            raise NotFound
        except Exception as error:
            return error
    
    async def album_artist():
        try:
            return album_selected['artists'][0]['name']
        except IndexError:
            raise NotFound
        except Exception as error:
            return error

    async def track_list():
        query = await spotify.album_tracks(album_id=album_selected['id'])
        track_list = query['items']
        tracks = []
        for track in track_list:
            tracks.append(track['name'])
        return tracks


    # The date the album was first released, for example “1981-12-15”. 
    # Depending on the precision, it might be shown as “1981” or “1981-12”.
    # The precision with which release_date value is known: “year” , “month” , or “day”.	
    async def get_release_date():
        album_release_date = album_selected['release_date']
        album_release_date_type = album_selected['release_date_precision']
        try:
            if album_release_date_type == "day":
               parsed_time = datetime.strptime(album_release_date, "%Y-%m-%d").strftime('%B %-d, %Y')
               return parsed_time
            elif album_release_date_type == "month":
                parsed_time = datetime.strptime(album_release_date, "%Y-%m").strftime('%B %Y')
                return parsed_time
            elif album_release_date_type == "year":
                return album_release_date
        except Exception:
            return "Unknown!"

    
    info = {"AlbumArtist": await album_artist(), "AlbumName": await get_album_name(), "AlbumCoverArt": await get_cover_art(), "URL": await get_url(), "TrackList": await track_list(), "ReleaseDate": await get_release_date()}
    return SpotifyAlbum(info)


class SpotifyAlbum(Album):

    def __init__(self, data:dict):
        self.color = 0x84bd00
        self.service = 'Spotify'
        self.name = data['AlbumName']
        self.artist = data['AlbumArtist']
        self.link = data['URL']
        self.track_list = data['TrackList']
        self.cover_url = data['AlbumCoverArt']
        self.release_date = data['ReleaseDate']

class SpotifySong(Song):

    def __init__(self, data:dict):
        self.color = 0x84bd00
        self.service = 'Spotify'
        self.name = data['TrackName']
        self.artist = data['TrackArtist']
        self.link = data['TrackURL']
        self.cover_url = data['TrackCoverArt']
        self.track_album = data['TrackAlbum']
        self.release_date = data['TrackReleaseDate']