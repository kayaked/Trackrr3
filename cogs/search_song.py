import aiohttp
import datetime
import random
import io
import traceback
import copy
import json

import discord
from discord.ext import commands
import motor.motor_asyncio
from mutagen import id3

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
import cogs.mods.bandcamp as bandcamp
import cogs.mods.napster as napster
import cogs.mods.pandora as pandora
import cogs.mods.youtube as youtube
import cogs.mods.base as base


client = motor.motor_asyncio.AsyncIOMotorClient()
db = client['Trackrr']
dev_picks = json.load(open('dev_notes.json', 'r', encoding='utf-8'))


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
            'pandora',
            'napster',
            'bandcamp',
            'youtube'
        ]

    # Basic support for search_playing
    @commands.command(name='search_playing', invoke_without_command=True)
    async def search_playing(self, ctx, member: discord.Member, service=''):
        # Section for how args are formatted.
        if isinstance(member, str) and not service:
            service = member
            member = ctx.author
        if not member:
            member = ctx.author

        if service.lower() in self.services or not service:
            user_activity = member.activity
            if isinstance(user_activity, discord.Spotify):

                form = {
                    "SongName": user_activity.title,
                    "SongArtist": user_activity.artist,
                    "SongAlbum": user_activity.album,
                    "TrackID": user_activity.track_id,
                    "SongAlbumCover": user_activity.album_cover_url
                }

                song_name = "{} {}".format(
                    form['SongName'], form['SongArtist'])

                await ctx.send("🎧 Here's what {} is currently listening to!".format(member.mention))

                cmd = self.bot.get_command('search_song')
                service_f = service + ' ' if service else ''
                await ctx.invoke(cmd, song_name="{}{}".format(service_f, song_name))

            else:
                await ctx.send("you're not listening to spotify.")

        else:
            await ctx.send('Service invalid!')

    @commands.group(name='search_song', invoke_without_command=True, aliases=['search', 'search_track', 'song', 'track', 'tracksearch', 'searchtrack', 'searchsong', 'songsearch', 'song_search', 'track_search'])
    async def search_song(self, ctx, *, song_name=None):
        try:
            svc = song_name.split(' ')[0].lower()
        except:
            svc = None
        # Paginator for all services.
        if svc == 'all' and song_name:

            current_service = await db.preferredsvc.find_one({'uid': ctx.author.id})

            if not current_service:
                current_service = 'spotify'
            else:
                current_service = current_service.get('service', 'spotify')
            async def get_embed():
                embed = discord.Embed()
                try:
                    song = await globals().get(current_service).search_song(' '.join(song_name.split(' ')[1:]))
                    embed = self.song_format(song)
                except base.NotFound:
                    embed = discord.Embed(title='Trackrr', description=f'No results found for `{current_service}`!')
                return embed
            async with ctx.channel.typing():
                m = await ctx.send(embed=await get_embed())
            emojis = []
            for service in self.services:
                if [emoji for emoji in self.bot.emojis if emoji.name == service.lower()]:
                    emojis.append([
                        emoji for emoji in self.bot.emojis if emoji.name == service.lower()][0])

            for eji in emojis:
                await m.add_reaction(eji)
            paging = True
            while paging:
                try:
                    reaction, user = await self.bot.wait_for('reaction_add', check=lambda r, u: r.message.id == m.id and u.id == ctx.author.id and r.emoji in emojis and not u.bot, timeout=10)
                    try:
                        await m.remove_reaction(reaction, user)
                    except:
                        pass
                    current_service = reaction.emoji.name
                    await m.edit(embed=discord.Embed(title='Trackrr', description=f'🔍 Loading `{current_service}`...'))
                    await m.edit(embed=await get_embed())
                except:
                    paging = False
                    for eji in emojis:
                        await m.remove_reaction(eji, ctx.guild.me)
                    return

        # Checks for a preferred service
        if svc and svc not in self.services and await db.preferredsvc.find_one({'uid':ctx.author.id}) and svc != 'list':
            svc = await db.preferredsvc.find_one({'uid': ctx.author.id})
            svc = svc.get('service', '')
            song_name = svc + ' ' + song_name

        #####
        if not song_name or svc not in self.services or svc == 'list':
            services = copy.deepcopy(self.services)
            for service in services:
                if [emoji for emoji in self.bot.emojis if emoji.name == service.lower()]:
                    emoji = [
                        emoji for emoji in self.bot.emojis if emoji.name == service.lower()][0]

                    services[services.index(service)] = f'<:{emoji.name}:{emoji.id}> ' + f'`{service}`'

            cmdprefix = (await self.bot.command_prefix(self.bot, ctx.message))[-1]
            services.append('🎵 `all`')
            services.insert(0, f'`{cmdprefix}{ctx.invoked_with} <service/all> <*song name>`')
            services.append(f'To use this command without a service, run `{cmdprefix}prefs service <service>` to set a default search service.')
            embed = discord.Embed(title=f'List of available services for {cmdprefix}search_song', description='\n'.join(services), timestamp=datetime.datetime.now(), color=random.randint(0x000000, 0xffffff))

            embed.set_footer(
                text="Trackrr Music Search",
                icon_url="https://media.discordapp.net/attachments/452763485743349761/452763575878942720/TrackrrLogo.png"
            )

            return await ctx.send(embed=embed)

        async with ctx.channel.typing():
            try:
                song = await globals().get(svc).search_song(' '.join(song_name.split(' ')[1:]))
            except base.NotFound:
                return await ctx.send(f'Result not found on {svc}!')
            embed = self.song_format(song)
            await ctx.send(embed=embed)

    def song_format(self, album):
        embed = discord.Embed(
            title=str(album.name),
            url=album.link,
            color=discord.Color(getattr(album, 'color', 0)),
            timestamp=datetime.datetime.now()
        )
        if [emoji for emoji in self.bot.emojis if emoji.name == getattr(album, 'service', 'aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa').lower()]:
            emoji = [emoji for emoji in self.bot.emojis if emoji.name == album.service.lower()][0]
            embed.title = embed.title + f' <:{emoji.name}:{emoji.id}>'
        if isinstance(album.release_date, datetime.datetime):
            album.release_date = album.release_date.strftime('%B %-d, %Y')

        embed.add_field(
            name='Name',
            value=album.name,
            inline=False
        )

        embed.add_field(
            name='Artist(s)',
            value=album.artist,
            inline=False
        )

        embed.add_field(
            name='Released',
            value=album.release_date,
            inline=False
        )

        try:
            dev_info = dev_picks[album.track_album]
            embed.add_field(
                name='Album',
                value=album.track_album,
                inline=False
            )

            embed.add_field(
                name="Dev Note",
                value=dev_info,
                inline=False
            )

        except Exception:
            embed.add_field(
                name='Album',
                value=album.track_album,
                inline=False
            )

        embed.set_footer(
            text=f"Trackrr Music Search | Data pulled from {album.service}",
            icon_url="https://media.discordapp.net/attachments/452763485743349761/452763575878942720/TrackrrLogo.png"
        )

        embed.set_thumbnail(url=album.cover_url)

        return embed

    @commands.command(name='upload_song', aliases=['upload_track'])
    async def upload_track(self, ctx, service=None):
        if not ctx.message.attachments:
            cmdprefix = (await self.bot.command_prefix(self.bot, ctx.message))[-1]
            embed = discord.Embed(
                color=random.randint(0x000000, 0xffffff),
                title=f'Help for `{cmdprefix}{ctx.invoked_with}`',
                description=f'`{cmdprefix}{ctx.invoked_with} [optional service] {"{ATTACHED MP3}"}`'
            )
            embed.set_image(
                url='https://cdn.discordapp.com/attachments/528057306185990175/529039264122404865/4f60da11f38df6119dea86b0fe2883a8.png'
            )
            embed.set_footer(
                text=f"Trackrr Music Search",
                icon_url="https://media.discordapp.net/attachments/452763485743349761/452763575878942720/TrackrrLogo.png"
            )
            return await ctx.send(embed=embed)

        async with aiohttp.ClientSession() as session:
            async with session.get(ctx.message.attachments[0].url) as resp:
                raw = await resp.read()

        raw = io.BytesIO(raw)

        raw = id3.ID3(raw)

        file_name = ', '.join(raw.get('TIT2').text)

        if not service:
            date = raw.get('TDRL')

            if not date:
                date = raw.get('TDRC')

            class TempTrack:
                link = ctx.message.attachments[0].url
                service = 'computer'
                name = file_name
                track_album = ', '.join(raw.get('TALB').text)
                cover_url = 'https://github.com/exofeel/Trackrr/blob/master/assets/UnknownCoverArt.png?raw=true'
                release_date = str(getattr(date, 'text', ['1970'])[0])
                artist = ', '.join(raw.get('TPE1').text)

            embed = self.song_format(TempTrack)
            embed.title = embed.title + ' 🖥'
            embed.set_footer(
                text="Trackrr Music Search | Data pulled from ID3 tags using Mutagen",
                icon_url="https://media.discordapp.net/attachments/452763485743349761/452763575878942720/TrackrrLogo.png"
            )

            file = {}

            if any([key.startswith('APIC:') for key in list(raw.keys())]):

                keyname = [key for key in list(
                    raw.keys()) if key.startswith('APIC')][0]

                buffer = io.BytesIO(raw.get(keyname).data)
                file['file'] = discord.File(buffer, filename="image.png")
                embed.set_thumbnail(url="attachment://image.png")
            else:
                embed.set_thumbnail(url='https://github.com/exofeel/Trackrr/blob/master/assets/UnknownCoverArt.png?raw=true')
            await ctx.send(**file, embed=embed)
        else:
            cmd = self.bot.get_command('search_song')
            await ctx.invoke(cmd, song_name="{} {}".format(service, file_name))


def setup(bot):
    bot.add_cog(SearchSong(bot))
