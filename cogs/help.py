def setup(bot):
    bot.add_cog(Help(bot))

import discord
import datetime
from discord.ext import commands
import random

faq = """

How often will this bot be updated?
A: It depends really on how busy/motivated we are.

How do you guys obtain the music info?
A: We have multiple methods, some of which are private as of now. If you have any questions, feel free to DM Yak#7474 or exofeel#3333.

What is your favorite album?
A: Probably KIDS SEE GHOSTS by Kanye x Cudi for both of us.

""".strip()

class Help:

    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='help', aliases=['support', 'info', 'botinfo'])
    async def _help(self, ctx):
        embed = discord.Embed(title='Trackrr 3', description='A Discord bot that searches music information anywhere, anytime.', timestamp=datetime.datetime.now(), color=random.randint(0x000000, 0xffffff))
        embed.set_thumbnail(url='https://cdn.discordapp.com/avatars/449305030802145280/14a07b4dee929f492871e814f0330af4.png?size=128')
        embed.add_field(name=f'`{self.bot.command_prefix}search_album` `<service/all>` `<*album name>`', value=f'Search for an album/mixtape on a specified service, or all services.\nRun `{self.bot.command_prefix}search_album` for a list of services.')
        embed.add_field(name=f'`{self.bot.command_prefix}search_song` `<service/all>` `<*song name>`', value=f'Search for an song/track on a specified service, or all services.\nRun `{self.bot.command_prefix}search_song` for a list of services.')
        embed.add_field(name=f'`{self.bot.command_prefix}search_artist` `<*artist name>`', value=f'Search for an artist and information about them.')
        embed.add_field(name=f'`{self.bot.command_prefix}upload_song` `[MP3 ATTACHMENT]`', value=f'Attach an MP3 file to your message and receive info about the song you uploaded.')
        embed.add_field(name=f'`{self.bot.command_prefix}help`', value=f'Shows this menu.')
        embed.set_footer(text=f'Trackrr')
        await ctx.send(embed=embed)

    @commands.command(name='faq', aliases=['questions', ])
    async def _faq(self, ctx):
        embed = discord.Embed(title='Trackrr 3 - Frequently Asked Questions', description=faq, timestamp=datetime.datetime.now(), color=random.randint(0x000000, 0xffffff))
        embed.set_footer(text=f'Trackrr')
        await ctx.send(embed=embed)

    @commands.command(name='ping', aliases=['latency', 'speed'])
    async def _ping(self, ctx):
        ping = round(self.bot.latency*1000)
        embed = discord.Embed(title='Trackrr Ping', description=f'<a:ping_heartbeat:521565184188219392> {ping}ms', color=random.randint(0x000000, 0xffffff))
        await ctx.send(embed=embed)