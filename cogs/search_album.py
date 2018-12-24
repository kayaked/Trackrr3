import discord
from discord.ext import commands
import aiohttp
import cogs.mods.genius as genius
import cogs.mods.soundcloud as soundcloud
import cogs.mods.lastfm as lastfm
import cogs.mods.itunes as itunes
import cogs.mods.tidal as tidal
import cogs.mods.spinrilla as spinrilla
import cogs.mods.musicbrainz as musicbrainz
import cogs.mods.deezer as deezer
import cogs.mods.mixtapemonkey as mixtapemonkey
import cogs.mods.playmusic as playmusic
import cogs.mods.spotify as spotify
import cogs.mods.base as base
import datetime

class SearchAlbum:

    def __init__(self, bot):
        self.bot = bot
        self.services = [
            'tidal',
            'lastfm',
            'mixtapemonkey',
            'musicbrainz',
            'soundcloud',
            'spinrilla',
            'spotify',
            'deezer',
            'genius',
            'itunes',
            'playmusic',
            'spotify'
        ]

    @commands.group(name='search_album', invoke_without_command=True)
    async def search_album(self, ctx, *, album_name=''):
        svc = album_name.split(' ')[0].lower()
        if not album_name or svc not in self.services:
            return await ctx.send(f'`{", ".join(self.services)}`')

        try:
            album = await globals().get(svc).search_album(' '.join(album_name.split(' ')[1:]))
        except base.NotFound:
            return await ctx.send(f'Result not found on {svc}!')
        embed = self.album_format(album)
        embed.set_footer(text=f'Information requested by user {ctx.author} • {ctx.author.id}')
        await ctx.send(embed=embed)

    def album_format(self, album):
        embed = discord.Embed(title=str(album.name), url=album.link, color=discord.Color(getattr(album, 'color', 0)), timestamp=datetime.datetime.today())
        if [emoji for emoji in self.bot.emojis if emoji.name == getattr(album, 'service', 'aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa').lower()]:
            emoji = [emoji for emoji in self.bot.emojis if emoji.name == album.service.lower()][0]
            embed.title = embed.title + f' <:{emoji.name}:{emoji.id}>'
        embed.add_field(name='Name', value=album.name, inline=False)
        embed.add_field(name='Artist(s)', value=album.artist, inline=False)
        embed.add_field(name='Released', value=album.release_date.strftime('%B %-d, %Y'), inline=False)
        embed.add_field(name='Track List', value='\n'.join(album.track_list).replace('*', r'\*') if album.track_list else 'Unknown', inline=False)
        embed.set_thumbnail(url=album.cover_url)

        return embed

def setup(bot):
    bot.add_cog(SearchAlbum(bot))