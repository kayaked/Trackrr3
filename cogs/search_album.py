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

class SearchAlbum:

    def __init__(self, bot):
        self.bot = bot

    @commands.group(name='search_album', invoke_without_command=True)
    async def search_album(self, ctx):
        await ctx.send(f'`{", ".join([cmd.name for cmd in ctx.command.commands])}`')

    def album_format(self, album):

        embed = discord.Embed(title=str(album.name), url=album.link, color=discord.Color(getattr(album, 'color', 0)))
        if [emoji for emoji in self.bot.emojis if emoji.name == getattr(album, 'service', 'aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa').lower()]:
            emoji = [emoji for emoji in self.bot.emojis if emoji.name == album.service.lower()][0]
            embed.title = embed.title + f' <:{emoji.name}:{emoji.id}>'
        embed.add_field(name='Name', value=album.name, inline=False)
        embed.add_field(name='Artist(s)', value=album.artist, inline=False)
        embed.add_field(name='Released', value=album.release_date.strftime('%B %-d, %Y'), inline=False)
        embed.add_field(name='Track List', value='\n'.join(album.track_list).replace('*', r'\*') if album.track_list else 'Unknown', inline=False)
        embed.set_thumbnail(url=album.cover_url)

        return embed

    @search_album.command(name='genius')
    async def sa_genius(self, ctx, *, album_name):

        album = await genius.search_album(album_name)
        embed = self.album_format(album)

        await ctx.send(embed=embed)

    @search_album.command(name='soundcloud')
    async def sa_soundcloud(self, ctx, *, album_name):

        album = await soundcloud.search_album(album_name)
        embed = self.album_format(album)

        await ctx.send(embed=embed)

    @search_album.command(name='lastfm')
    async def sa_lastfm(self, ctx, *, album_name):

        album = await lastfm.search_album(album_name)
        embed = self.album_format(album)

        await ctx.send(embed=embed)

    @search_album.command(name='itunes')
    async def sa_itunes(self, ctx, *, album_name):

        album = await itunes.search_album(album_name)
        embed = self.album_format(album)

        await ctx.send(embed=embed)

    @search_album.command(name='tidal')
    async def sa_tidal(self, ctx, *, album_name):

        album = await tidal.search_album(album_name)
        embed = self.album_format(album)

        await ctx.send(embed=embed)

    @search_album.command(name='spinrilla')
    async def sa_spinrilla(self, ctx, *, album_name):

        album = await spinrilla.search_album(album_name)
        embed = self.album_format(album)

        await ctx.send(embed=embed)

    @search_album.command(name='musicbrainz')
    async def sa_musicbrainz(self, ctx, *, album_name):

        album = await musicbrainz.search_album(album_name)
        embed = self.album_format(album)

        await ctx.send(embed=embed)

    @search_album.command(name='deezer')
    async def sa_deezer(self, ctx, *, album_name):

        album = await deezer.search_album(album_name)
        embed = self.album_format(album)

        await ctx.send(embed=embed)

def setup(bot):
    bot.add_cog(SearchAlbum(bot))