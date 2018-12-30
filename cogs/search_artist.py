import discord
from discord.ext import commands
import cogs.mods.itunes as itunes
import cogs.mods.base as base

class ArtistSearch:

    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='search_artist', aliases=['creator', 'artist', 'person', 'musician', 'people', 'search_person', 'search_musician', 'search_creator', 'searchartist', 'artist_search'])
    async def search_artist(self, ctx, *, artist_name=None):
        if not artist_name:
            cmdprefix = (await self.bot.command_prefix(self.bot, ctx.message))[-1]
            embed = discord.Embed(title=f'Help for `{cmdprefix}{ctx.invoked_with}`', description=f'`{cmdprefix}{ctx.invoked_with} <artist name>`')
            embed.set_footer(text="Trackrr Music Search", icon_url="https://media.discordapp.net/attachments/452763485743349761/452763575878942720/TrackrrLogo.png")
            return await ctx.send(embed=embed)
        async with ctx.channel.typing():
            try:
                embed = await itunes.search_artist(artist_name)
            except base.NotFound:
                embed = discord.Embed(title=f'Trackrr', description=f'No results found for `{artist_name}`!')
            embed.set_footer(text="Trackrr Music Search | Data pulled from Apple Music", icon_url="https://media.discordapp.net/attachments/452763485743349761/452763575878942720/TrackrrLogo.png")
            await ctx.send(embed=embed)

def setup(bot):
    bot.add_cog(ArtistSearch(bot))