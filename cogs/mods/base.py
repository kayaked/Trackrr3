
class Album:

    __slots__ = ('name', 'track_list', 'artist', 'link', 'release_date', 'cover_url', 'color', 'service')

class NotFound(Exception):
    pass