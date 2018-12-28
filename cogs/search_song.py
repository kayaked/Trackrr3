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
import traceback
from mutagen import id3
import copy

class SearchSong:

    def __init__(self, bot):
        self.bot = bot
        self.services = [
            'spotify',
            'itunes',
            'soundcloud',
            'amazon',
            'deezer',
            'genius',
            'tidal',
            'lastfm',
            'spinrilla',
            'pandora'
        ]

    @commands.group(name='search_song', invoke_without_command=True, aliases=['search_track', 'song', 'track', 'tracksearch', 'searchtrack', 'searchsong', 'songsearch', 'song_search'])
    async def search_song(self, ctx, *, song_name='a'):
        svc = song_name.split(' ')[0].lower()
        # Paginator for all services.
        if svc == 'all' and song_name:
            index = 0
            async def get_embed():
                embed = discord.Embed()
                try:
                    song = await globals().get(self.services[index]).search_song(' '.join(song_name.split(' ')[1:]))
                    embed = self.song_format(song)
                except base.NotFound:
                    embed = discord.Embed(title='Trackrr', description=f'No results found for `{self.services[index]}`!')
                embed.add_field(name=r'\⬅', value=self.services[index-1 if index else -1])
                embed.add_field(name=r'\➡', value=self.services[index+1 if index+1 < len(self.services) else 0])
                return embed
            async with ctx.channel.typing():
                m=await ctx.send(embed=await get_embed())
            await m.add_reaction('⬅')
            await m.add_reaction('➡')
            emojis = ['⬅', '➡']
            paging=True
            while paging:
                try:
                    reaction, user = await self.bot.wait_for('reaction_add', check=lambda r, u: str(r.emoji) in emojis and not u.bot, timeout=10)
                    try:
                        await m.remove_reaction(reaction, user)
                    except:
                        pass
                    if str(reaction.emoji) == '⬅':
                        if index:
                            index-=1
                        else:
                            index=len(self.services)-1
                    if str(reaction.emoji) == '➡':
                        if index+1 < len(self.services):
                            index+=1
                        else:
                            index=0
                    await m.edit(embed=discord.Embed(title='Trackrr', description=f'🔍 Loading `{self.services[index]}`...'))
                    await m.edit(embed=await get_embed())
                except:
                    paging=False
                    await m.remove_reaction('⬅', ctx.guild.me)
                    await m.remove_reaction('➡', ctx.guild.me)
                    embed=m.embeds[0]
                    embed.remove_field(-1)
                    embed.remove_field(-1)
                    await m.edit(embed=embed)
                    return
        #####
        if not song_name or svc not in self.services:
            services = copy.deepcopy(self.services)
            for service in services:
                if [emoji for emoji in self.bot.emojis if emoji.name == service.lower()]:
                    emoji = [emoji for emoji in self.bot.emojis if emoji.name == service.lower()][0]
                    services[services.index(service)] = f'<:{emoji.name}:{emoji.id}> ' + f'`{service}`'
            services.append('🎵 `all`')
            embed = discord.Embed(title=f'List of available services for {self.bot.command_prefix}search_song', description='\n'.join(services), timestamp=datetime.datetime.now(), color=random.randint(0x000000, 0xffffff))
            embed.set_footer(text="Trackrr Music Search", icon_url="https://media.discordapp.net/attachments/452763485743349761/452763575878942720/TrackrrLogo.png")
            return await ctx.send(embed=embed)

        async with ctx.channel.typing():
            try:
                song = await globals().get(svc).search_song(' '.join(song_name.split(' ')[1:]))
            except base.NotFound:
                return await ctx.send(f'Result not found on {svc}!')
            embed = self.song_format(song)
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
        embed.set_footer(text=f"Trackrr Music Search | Data pulled from {album.service}", icon_url="https://media.discordapp.net/attachments/452763485743349761/452763575878942720/TrackrrLogo.png")
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
        embed.set_footer(text="Trackrr Music Search | Data pulled from ID3 tags using Mutagen", icon_url="https://media.discordapp.net/attachments/452763485743349761/452763575878942720/TrackrrLogo.png")
        file = {}
        if any([key.startswith('APIC:') for key in list(raw.keys())]):
            keyname = [key for key in list(raw.keys()) if key.startswith('APIC')][0]
            buffer = io.BytesIO(raw.get(keyname).data)
            file['file'] = discord.File(buffer, filename="image.png")
            embed.set_thumbnail(url="attachment://image.png")
        else:
            embed.set_thumbnail(url='https://github.com/exofeel/Trackrr/blob/master/assets/UnknownCoverArt.png?raw=true')
        await ctx.send(**file, embed=embed)
        

def setup(bot):
    bot.add_cog(SearchSong(bot))