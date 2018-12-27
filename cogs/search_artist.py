import discord
from discord.ext import commands
import cogs.mods.itunes as itunes
import cogs.mods.base as base

class ArtistSearch:

    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='search_artist', aliases=['creator', 'artist', 'person', 'musician', 'people', 'search_person', 'search_musician', 'search_creator'])
    async def search_artist(self, ctx, *, artist_name):
        async with ctx.channel.typing():
            try:
                embed = await itunes.search_artist(artist_name)
            except base.NotFound:
                embed = discord.Embed(title=f'Trackrr', description=f'No results found for `{artist_name}`!')
            embed.set_footer(text=f'Information requested by user {ctx.author} • {ctx.author.id}')
            await ctx.send(embed=embed)

def setup(bot):
    bot.add_cog(ArtistSearch(bot))