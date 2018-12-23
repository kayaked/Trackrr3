from pyfy import AsyncSpotify
#from .keys import SPOTIFYSECRET, SPOTIFYCLIENT, SPOTIFYSCOPE, SPOTIFYNAME, SPOTIFYREDIRECTURL
#from .base import Album
from base import Album
from keys import Keys


# Ported from TrackrrV1-V2
# Now using PyFy async lib

class NotFound(Exception):
    pass

async def authorize_spotify():
    """ Authoirzies Spotify using PyFy's Method """
    from pyfy import ClientCreds
    client = ClientCreds(client_id=Keys.SPOTIFYCLIENT, client_secret=Keys.SPOTIFYSECRET)
    spotify = AsyncSpotify(client_creds=client)
    await spotify.authorize_client_creds()
    return await spotify



async def search_album(album_name):
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
    
    info = {"AlbumArtist": await album_artist(), "AlbumName": await get_album_name(), "AlbumCoverArt": await get_cover_art(), "URL": await get_url(), "TrackList": await track_list()}
    return info


class SpotifyAlbum(Album):

    def __init__(self, data:dict):
        self.name = data['AlbumName']
        self.artist = data['AlbumArtist']
        self.link = data['URL']
        self.track_list = data['TrackList']
        self.cover_url = data['AlbumCoverArt']