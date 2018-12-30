
class Album:

    __slots__ = ('name', 'track_list', 'artist', 'link', 'release_date', 'cover_url', 'color', 'service')


class Song:

    __slots__ = {'name', 'artist', 'link', 'cover_url', 'release_date', 'track_album', 'color', 'service'}


# For Spotify Discord

class SpotifyDiscordSong:

	__slots__ = {'track_name', 'track_artist', 'track_album', 'track_id'}

class NotFound(Exception):
    pass