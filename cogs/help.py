import discord
import datetime
from discord.ext import commands
import random


def setup(bot):
    bot.add_cog(Help(bot))

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
    @commands.cooldown(10, 10, commands.BucketType.guild)
    @commands.cooldown(3, 10, commands.BucketType.user)
    async def _help(self, ctx, page='1'):
        cmdprefix = (await self.bot.command_prefix(self.bot, ctx.message))[-1]
        embed = discord.Embed(title='Trackrr 3', description='A Discord bot that searches music information anywhere, anytime.', timestamp=datetime.datetime.now(), color=random.randint(0x000000, 0xffffff))
        embed.set_thumbnail(
            url='https://cdn.discordapp.com/avatars/449305030802145280/14a07b4dee929f492871e814f0330af4.png?size=128'
        )
        if page == '1':
            embed.add_field(
                name=f'`{cmdprefix}search_album` `<service/all>` `<*album name>`',
                value=f'Search for an album/mixtape on a specified service, or all services.\nRun `{cmdprefix}search_album` for a list of services.'
            )
            embed.add_field(
                name=f'`{cmdprefix}search_song` `<service/all>` `<*song name>`',
                value=f'Search for an song/track on a specified service, or all services.\nRun `{cmdprefix}search_song` for a list of services.'
            )
            embed.add_field(
                name=f'`{cmdprefix}search_artist` `<*artist name>`',
                value=f'Search for an artist and information about them.'
            )
            embed.add_field(
                name=f'`{cmdprefix}upload_song` `<optional service>` `[MP3 ATTACHMENT]`',
                value=f'Attach an MP3 file to your message and receive info about the song you uploaded (optionally search it on a music service if you provide one).'
            )
            embed.add_field(
                name=f'`{cmdprefix}prefs`',
                value=f'Preference menu for Trackrr. Has options for the current guild and user, such as the guild\'s current prefix.\n\nDo `{cmdprefix}help 2` to view the next page of commands.'
            )
        elif page == '2':
            embed.add_field(
                name=f'`{cmdprefix}lyrics` `<*song name>`',
                value=f'Scans lyrics from Genius for a song.'
            )
            embed.add_field(
                name=f'`{cmdprefix}charts/{cmdprefix}trending/{cmdprefix}viral` `<optional "albums">`',
                value=f'Gets either charts from Billboard, the trending 50 on genius, or Spotify\'s viral 50. Album charts can also be viewed on Genius and Billboard.'
            )
            embed.add_field(
                name=f'`{cmdprefix}producer_tag` `<*producer name>`',
                value=f'Finds a producer\'s tag.'
            )
            embed.add_field(
                name=f'`{cmdprefix}search_playing` `<Member> <service>`',
                value=f'Gets the song that a user is currently playing and search it, just like `{cmdprefix}search_song` does.'
            )
            embed.add_field(
                name=f'`{cmdprefix}help`',
                value=f'Shows this menu.\n\nDo `{cmdprefix}help 3` to view the next page of commands.'
            )
        elif page == '3':
            embed.add_field(
                name=f'`Favoriting tracks`',
                value='To favorite a track, search it and then react to the result message with a ❤️. Trackrr will then save the song to your favorites! (Does not work on albums)'
            )
            embed.add_field(
                name=f'`{cmdprefix}favorites`',
                value=f'Lists your favorite songs. You can also provide a number (`{cmdprefix}favorites <#>`) to view a track you have favorited.'
            )
            embed.add_field(
                name=f'`{cmdprefix}remove_favorite` `<#>`',
                value='Removes a favorite song by its number on your favorites list.'
            )
            embed.add_field(
                name=f'`{cmdprefix}analyze`',
                value='Gets sound and tune info about the current track your are listening to. (Spotify presence)'
            )
        embed.set_footer(
            text="Trackrr Music Search | Created by exofeel#3333 X Yak#7474",
            icon_url="https://media.discordapp.net/attachments/452763485743349761/452763575878942720/TrackrrLogo.png"
        )
        await ctx.send(embed=embed)

    @commands.command(name='faq', aliases=['questions'])
    async def _faq(self, ctx):
        embed = discord.Embed(title='Trackrr 3 - Frequently Asked Questions', description=faq, timestamp=datetime.datetime.now(), color=random.randint(0x000000, 0xffffff))
        embed.set_footer(text="Trackrr Music Search | Created by exofeel#3333 X Yak#7474", icon_url="https://media.discordapp.net/attachments/452763485743349761/452763575878942720/TrackrrLogo.png")
        await ctx.send(embed=embed)

    @commands.command(name='ping', aliases=['latency', 'speed'])
    async def _ping(self, ctx):
        ping = round(self.bot.latency*1000)
        embed = discord.Embed(title=f'Trackrr {ctx.invoked_with.capitalize()}', description=f'<a:ping_heartbeat:521565184188219392> {ping}ms', color=random.randint(0x000000, 0xffffff))
        await ctx.send(embed=embed)
