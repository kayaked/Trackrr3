def setup(bot):
    bot.add_cog(Help(bot))

import discord
import datetime
from discord.ext import commands
import random

class Help:

    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='help')
    async def _help(self, ctx):
        embed = discord.Embed(title='Trackrr 3', description='A Discord bot that searches music information anywhere, anytime.', timestamp=datetime.datetime.now(), color=random.randint(0x000000, 0xffffff))
        embed.set_thumbnail(url='https://cdn.discordapp.com/avatars/449305030802145280/14a07b4dee929f492871e814f0330af4.png?size=128')
        embed.add_field(name=f'`{self.bot.command_prefix}search_album` `<service>` `<*name>`', value=f'Search for an album/mixtape on a specified service.\nRun `{self.bot.command_prefix}album_search` for a list of services.')
        embed.add_field(name=f'`{self.bot.command_prefix}help`', value=f'Shows this menu')
        embed.set_footer(text=f'Information requested by user {ctx.author} • {ctx.author.id}')
        await ctx.send(embed=embed)