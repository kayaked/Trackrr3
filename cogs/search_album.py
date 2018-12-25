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
import cogs.mods.googleplay as googleplay
import cogs.mods.spotify as spotify
import cogs.mods.base as base
import cogs.mods.amazon as amazon
import cogs.mods.bandcamp as bandcamp
import datetime
import random

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
            'googleplay',
            'spotify',
            'amazon',
            'bandcamp'
        ]

    @commands.group(name='search_album', invoke_without_command=True)
    async def search_album(self, ctx, *, album_name=''):
        svc = album_name.split(' ')[0].lower()
        if not album_name or svc not in self.services:
            services = self.services
            for service in services:
                if [emoji for emoji in self.bot.emojis if emoji.name == service.lower()]:
                    emoji = [emoji for emoji in self.bot.emojis if emoji.name == service.lower()][0]
                    services[services.index(service)] = f'<:{emoji.name}:{emoji.id}> ' + service
            embed = discord.Embed(title=f'List of available services for {self.bot.command_prefix}search_album', description='\n'.join(services), timestamp=datetime.datetime.now(), color=random.randint(0x000000, 0xffffff))
            embed.set_footer(text=f'Information requested by user {ctx.author} • {ctx.author.id}')
            return await ctx.send(embed=embed)

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