import discord
from discord.ext import commands
import motor.motor_asyncio
import copy
import traceback
import random
import math
import datetime
import cogs.mods.base as base


class GeneralSong(base.Song):
    def __init__(self, data: dict):
        self.name = data['name']
        self.artist = data['artist']
        self.release_date = data['release_date']
        self.track_album = data['track_album']
        self.link = data['link']
        self.service = data['service']
        self.color = 0xffffff
        self.cover_url = data['cover_url']

client = motor.motor_asyncio.AsyncIOMotorClient()
db = client['Trackrr']


class FavoriteSongs:

    def __init__(self, bot):
        self.bot = bot

    def is_favorite_reaction(self, reaction):
        if reaction.message.author.id != self.bot.user.id:
            return False
        if str(reaction.emoji) != '❤':
            return False
        msg = reaction.message
        if not msg.embeds:
            return False
        if not getattr(msg.embeds[0].footer, 'text'):
            return False
        if not isinstance(msg.embeds[0].fields, list):
            return False
        fields = [field.name for field in msg.embeds[0].fields]
        if any([
            'Name' not in fields,
            'Artist(s)' not in fields,
            'Album' not in fields,
            'Released' not in fields
        ]):
            return False
        return True

    async def on_reaction_add(self, reaction, user):
        if not self.is_favorite_reaction(reaction):
            return
        msg = reaction.message
        embed = msg.embeds[0]
        fields = embed.fields
        name = [field for field in fields if field.name == 'Name'][0].value
        artist = [field for field in fields if field.name == 'Artist(s)'][0].value
        release_date = [field for field in fields if field.name == 'Released'][0].value
        album = [field for field in fields if field.name == 'Album'][0].value
        cover_url = embed.thumbnail.url if isinstance(embed.thumbnail.url, str) else ''
        service = embed.footer.text.rsplit(' ', 1)[-1]
        url = str(embed.url)
        structure = {
            'uid': user.id,
            'name': name,
            'cover_url': cover_url,
            'track_album': album,
            'release_date': release_date,
            'artist': artist,
            'service': service,
            'link': url
        }
        if not await db.favorites.find_one(structure):
            await db.favorites.insert_one(structure)
        await reaction.message.channel.send(f'{user.mention} **{name} by {artist}** was added to your favorites!', delete_after=2)

    @commands.command(name='remove_favorite')
    async def remove_favorite(self, ctx, index):
        favorite = await db.favorites.find({'uid': ctx.author.id}).to_list(length=None)
        try:
            song_raw = favorite[int(index)-1]
            song = GeneralSong(song_raw)
        except (TypeError, IndexError):
            cmdprefix = (await self.bot.command_prefix(self.bot, ctx.message))[-1]
            message = f'Error: Number not a number, or not found in your favorites!\nPlease run `{cmdprefix}{ctx.invoked_with}` for a list of your favorites.'
            embed = discord.Embed(title='Trackrr Music Search', description=message)
            embed.set_footer(text="Trackrr Music Search", icon_url="https://media.discordapp.net/attachments/452763485743349761/452763575878942720/TrackrrLogo.png")
            return await ctx.send(embed=embed)
        await db.favorites.delete_many(song_raw)
        await ctx.send(f'{ctx.author.mention} OK, **{song.name} by {song.artist}** was removed from your favorites!', delete_after=2)

    @commands.command(name='favorites')
    @commands.cooldown(5, 3, commands.BucketType.guild)
    @commands.cooldown(1, 4, commands.BucketType.user)
    async def favorites_list(self, ctx, index=None):
        if index is None:
            favorite = await db.favorites.find({'uid': ctx.author.id}).to_list(length=None)
            albums = [GeneralSong(f) for f in favorite]
            cmdprefix = (await self.bot.command_prefix(self.bot, ctx.message))[-1]
            embedf = discord.Embed(title='Favorites ❤️', description=f'Here are some songs you\'ve selected as your personal favorites.\nUse `{cmdprefix}{ctx.invoked_with} <number>` to view a favorite (numbers are listed).')
            page = 0
            embed = self.favorites_embed_format(copy.deepcopy(embedf), albums, page)
            msg = await ctx.send(embed=embed)
            paging = True
            reactions = ['⬅', '➡']
            for reaction in reactions:
                await msg.add_reaction(reaction)
            while paging:
                try:
                    r, user = await self.bot.wait_for('reaction_add', check=lambda r, u: msg.id == r.message.id and u.id == ctx.author.id and str(r.emoji) in reactions and not u.bot, timeout=25)
                    user
                    if str(r.emoji) == '⬅':
                        if page == 0:
                            page = math.ceil(len(albums)/5)-1
                        else:
                            page -= 1
                    elif str(r.emoji) == '➡':
                        if (page+1)*5 > len(albums)-1:
                            page = 0
                        else:
                            page += 1
                    embed = self.favorites_embed_format(copy.deepcopy(embedf), albums, page)
                    await msg.edit(embed=embed)
                except:
                    paging = False
                    for reaction in reactions:
                        await msg.remove_reaction(reaction, ctx.guild.me)
        else:
            favorite = await db.favorites.find({'uid': ctx.author.id}).to_list(length=None)
            try:
                song = GeneralSong(favorite[int(index)-1])
            except (TypeError, IndexError):
                cmdprefix = (await self.bot.command_prefix(self.bot, ctx.message))[-1]
                message = f'Error: Number not a number, or not found in your favorites!\nPlease run `{cmdprefix}{ctx.invoked_with}` for a list of your favorites.'
                embed = discord.Embed(title='Trackrr Music Search', description=message)
                embed.set_footer(text="Trackrr Music Search", icon_url="https://media.discordapp.net/attachments/452763485743349761/452763575878942720/TrackrrLogo.png")
                return await ctx.send(embed=embed)
            embed = self.bot.get_cog('SearchSong').song_format(song)
            await ctx.send(embed=embed)

    def favorites_embed_format(self, embed, favorites, page):
        for i in favorites[page*5:(page*5)+5]:
            service = i.service
            if [emoji for emoji in self.bot.emojis if emoji.name == i.service.lower()]:
                emoji = [emoji for emoji in self.bot.emojis if emoji.name == i.service.lower()][0]
                service = f' <:{emoji.name}:{emoji.id}>'
            embed.add_field(name=f'{favorites.index(i)+1}. **{i.name}** by **{i.artist}**', value=f'{i.release_date} - on {i.track_album} - {service}', inline=False)
        if not favorites:
            embed.description += '\n\n(no favorites yet)'
        embed.set_footer(text="Trackrr Music Search", icon_url="https://media.discordapp.net/attachments/452763485743349761/452763575878942720/TrackrrLogo.png")
        return embed


def setup(bot):
    bot.add_cog(FavoriteSongs(bot))