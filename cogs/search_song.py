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
import cogs.mods.googleplay as googleplay
import cogs.mods.spotify as spotify
import cogs.mods.amazon as amazon
import cogs.mods.pandora as pandora
import cogs.mods.base as base
import datetime
import random
import io
from mutagen import id3
import copy

class SearchSong:

    def __init__(self, bot):
        self.bot = bot
        self.services = [
            'spotify',
            'spinrilla',
            'tidal',
            'deezer',
            'soundcloud',
            'genius',
            'lastfm',
            'amazon',
            'itunes',
            'pandora'
        ]

    @commands.group(name='search_song', invoke_without_command=True, aliases=['search_track', 'song', 'track', 'tracksearch', 'searchtrack', 'searchsong', 'songsearch', 'song_search'])
    async def search_song(self, ctx, *, album_name='a'):
        svc = album_name.split(' ')[0].lower()
        if not album_name or svc not in self.services:
            services = copy.deepcopy(self.services)
            for service in services:
                if [emoji for emoji in self.bot.emojis if emoji.name == service.lower()]:
                    emoji = [emoji for emoji in self.bot.emojis if emoji.name == service.lower()][0]
                    services[services.index(service)] = f'<:{emoji.name}:{emoji.id}> ' + service
            embed = discord.Embed(title=f'List of available services for {self.bot.command_prefix}search_song', description='\n'.join(services), timestamp=datetime.datetime.now(), color=random.randint(0x000000, 0xffffff))
            embed.set_footer(text=f'Information requested by user {ctx.author} • {ctx.author.id}')
            return await ctx.send(embed=embed)

        try:
            album = await globals().get(svc).search_song(' '.join(album_name.split(' ')[1:]))
        except base.NotFound:
            return await ctx.send(f'Result not found on {svc}!')
        embed = self.song_format(album)
        embed.set_footer(text=f'Information requested by user {ctx.author} • {ctx.author.id}')
        await ctx.send(embed=embed)

    def song_format(self, album):
        embed = discord.Embed(title=str(album.name), url=album.link, color=discord.Color(getattr(album, 'color', 0)), timestamp=datetime.datetime.now())
        if [emoji for emoji in self.bot.emojis if emoji.name == getattr(album, 'service', 'aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa').lower()]:
            emoji = [emoji for emoji in self.bot.emojis if emoji.name == album.service.lower()][0]
            embed.title = embed.title + f' <:{emoji.name}:{emoji.id}>'
        embed.add_field(name='Name', value=album.name, inline=False)
        embed.add_field(name='Artist(s)', value=album.artist, inline=False)
        embed.add_field(name='Released', value=album.release_date.strftime('%B %-d, %Y'), inline=False)
        embed.add_field(name='Album', value=album.track_album, inline=False)
        embed.set_thumbnail(url=album.cover_url)

        return embed
    
    @commands.command(name='upload_song', aliases=['upload_track'])
    async def upload_track(self, ctx, service=None):
        if not ctx.message.attachments:
            return await ctx.send('Please attach a file!')
        
        async with aiohttp.ClientSession() as session:
            async with session.get(ctx.message.attachments[0].url) as resp:
                raw = await resp.read()

        raw = io.BytesIO(raw)

        raw=id3.ID3(raw)

        date = raw.get('TDRL')

        if not date:
            date = raw.get('TDRC')

        class TempTrack:
            link = ctx.message.attachments[0].url
            service = 'computer'
            name = ', '.join(raw.get('TIT2').text)
            track_album = ', '.join(raw.get('TALB').text)
            cover_url = 'https://github.com/exofeel/Trackrr/blob/master/assets/UnknownCoverArt.png?raw=true'
            release_date = datetime.datetime.strptime(str(getattr(date, 'text', ['1970'])[0]), '%Y')
            artist = ', '.join(raw.get('TPE1').text)
        embed = self.song_format(TempTrack)
        embed.title = embed.title + ' 🖥'
        embed.set_footer(text=f'Information requested by user {ctx.author} • {ctx.author.id}')

        if raw.get('APIC:'):
            buffer = io.BytesIO(raw.get('APIC:').data)
            f = discord.File(buffer, filename="image.png")
            embed.set_thumbnail(url="attachment://image.png")
        else:
            embed.set_thumbnail(url='https://github.com/exofeel/Trackrr/blob/master/assets/UnknownCoverArt.png?raw=true')
        await ctx.send(file=f, embed=embed)
        

def setup(bot):
    bot.add_cog(SearchSong(bot))