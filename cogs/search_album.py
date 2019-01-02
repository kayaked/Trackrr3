import aiohttp
import copy
import datetime
import traceback
import random

import discord
from discord.ext import commands
import motor.motor_asyncio

import cogs.mods.genius as genius
import cogs.mods.soundcloud as soundcloud
import cogs.mods.lastfm as lastfm
import cogs.mods.itunes as itunes
import cogs.mods.tidal as tidal
import cogs.mods.spinrilla as spinrilla
import cogs.mods.musicbrainz as musicbrainz
import cogs.mods.deezer as deezer
import cogs.mods.youtube as youtube
import cogs.mods.mixtapemonkey as mixtapemonkey
import cogs.mods.googleplay as googleplay
import cogs.mods.spotify as spotify
import cogs.mods.base as base
import cogs.mods.napster as napster
import cogs.mods.amazon as amazon
import cogs.mods.bandcamp as bandcamp

client = motor.motor_asyncio.AsyncIOMotorClient()
db = client['Trackrr']


class SearchAlbum:

    def __init__(self, bot):
        self.bot = bot
        self.services = [
            'spotify',
            'itunes',
            'soundcloud',
            'amazon',
            'lastfm',
            'genius',
            'tidal',
            'googleplay',
            'deezer',
            'bandcamp',
            'spinrilla',
            'musicbrainz',
            'mixtapemonkey',
            'napster',
            'youtube'
        ]

    @commands.group(name='search_album', invoke_without_command=True, aliases=['album', 'searchalbum', 'albumsearch', 'album_search'])
    @commands.cooldown(5, 1, commands.BucketType.user)
    async def search_album(self, ctx, *, album_name=''):
        try:
            svc = album_name.split(' ')[0].lower()
        except:
            svc = None
        # Paginator for all services.
        if svc == 'all' and album_name:
            current_service = await db.preferredsvc.find_one({'uid': ctx.author.id})
            if not current_service:
                current_service = 'spotify'
            else:
                current_service = current_service.get('service', 'spotify')
            async def get_embed():
                embed = discord.Embed()
                try:
                    album = await globals().get(current_service).search_album(' '.join(album_name.split(' ')[1:]))
                    embed = self.album_format(album)
                except base.NotFound:
                    embed = discord.Embed(title='Trackrr', description=f'No results found for `{current_service}`!')
                return embed
            async with ctx.channel.typing():
                m = await ctx.send(embed=await get_embed())
            emojis = []
            for service in self.services:
                if [emoji for emoji in self.bot.emojis if emoji.name == service.lower()]:
                    emojis.append([emoji for emoji in self.bot.emojis if emoji.name == service.lower()][0])
            for eji in emojis:
                await m.add_reaction(eji)

            paging = True

            while paging is True:
                try:
                    reaction, user = await self.bot.wait_for('reaction_add', check=lambda r, u: r.message.id == m.id and u.id == ctx.author.id and r.emoji in emojis and not u.bot, timeout=25)
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
        #####

        # Checks for a preferred service
        if svc and svc not in self.services and await db.preferredsvc.find_one({'uid': ctx.author.id}):
            svc = await db.preferredsvc.find_one({'uid': ctx.author.id})
            svc = svc.get('service', '')
            album_name = svc + ' ' + album_name

        # Checks if the category is invalid, and provides a list of sources.
        if not album_name or svc not in self.services or svc == 'list':
            services = copy.deepcopy(self.services)
            for service in services:
                if [emoji for emoji in self.bot.emojis if emoji.name == service.lower()]:
                    emoji = [emoji for emoji in self.bot.emojis if emoji.name == service.lower()][0]
                    services[services.index(service)] = f'<:{emoji.name}:{emoji.id}> ' + f'`{service}`'

            cmdprefix = (await self.bot.command_prefix(self.bot, ctx.message))[-1]
            services.append('🎵 `all`')
            services.insert(0, f'`{cmdprefix}{ctx.invoked_with} <service/all> <*album name>`')
            services.append(f'To use this command without a service, run `{cmdprefix}prefs service <service>` to set a default search service.')

            embed = discord.Embed(
                title=f'List of available services for {cmdprefix}search_album',
                description='\n'.join(services), timestamp=datetime.datetime.now(),
                color=random.randint(0x000000, 0xffffff)
            )

            embed.set_footer(
                text="Trackrr Music Search",
                icon_url="https://media.discordapp.net/attachments/452763485743349761/452763575878942720/TrackrrLogo.png"
            )

            return await ctx.send(embed=embed)
        ####

        # Gets the album info by category.
        async with ctx.channel.typing():
            try:
                album = await globals().get(svc).search_album(' '.join(album_name.split(' ')[1:]))
            except base.NotFound:
                return await ctx.send(f'Result not found on {svc}!')
            embed = self.album_format(album)
            await ctx.send(embed=embed)

    def album_format(self, album):
        embed = discord.Embed(title=str(album.name), url=album.link, color=discord.Color(getattr(album, 'color', 0)), timestamp=datetime.datetime.today())
        if [emoji for emoji in self.bot.emojis if emoji.name == getattr(album, 'service', ' ').lower()]:

            emoji = [
                emoji for emoji in self.bot.emojis if emoji.name == album.service.lower()][0]

            embed.title = embed.title + f' <:{emoji.name}:{emoji.id}>'

        if isinstance(album.release_date, datetime.datetime):
            album.release_date = album.release_date.strftime('%B %-d, %Y')
        embed.add_field(name='Name', value=album.name, inline=False)
        embed.add_field(name='Artist(s)', value=album.artist, inline=False)
        embed.add_field(name='Released', value=album.release_date, inline=False)
        embed.add_field(name='Track List', value='\n'.join(album.track_list).replace('*', r'\*') if album.track_list else 'Unknown', inline=False)
        embed.set_footer(text=f"Trackrr Music Search | Data pulled from {album.service}", icon_url="https://media.discordapp.net/attachments/452763485743349761/452763575878942720/TrackrrLogo.png")
        embed.set_thumbnail(url=album.cover_url)

        return embed


def setup(bot):
    bot.add_cog(SearchAlbum(bot))
