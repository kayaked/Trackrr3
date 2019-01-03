import discord
from discord.ext import commands
import motor.motor_asyncio
import copy
import random
import datetime
import urllib.parse

client = motor.motor_asyncio.AsyncIOMotorClient()
db = client['Trackrr']


class Profiles:

    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='profile')
    @commands.cooldown(1, 2, commands.BucketType.user)
    @commands.cooldown(5, 5, commands.BucketType.guild)
    async def profile(self, ctx, user: discord.Member=None):
        if not user:
            user = ctx.author

        favorite_song = await db.favorites.find({'uid': user.id}).to_list(length=None)
        if favorite_song:
            favorite_song_final = random.choice(favorite_song)
            favorite_song_final = f'{favorite_song_final["name"]} by {favorite_song_final["artist"]}'
        else:
            favorite_song_final = 'Unknown'
        prefs = await db.preferredsvc.find_one({'uid': user.id})
        if prefs:
            if prefs.get('service'):
                svc = prefs['service']
                the_emoji = [emoji for emoji in self.bot.support_server.emojis if emoji.name == svc]
                if the_emoji:
                    svc = str(the_emoji[0]) + f' ({svc})'
            else:
                svc = 'N/A (not set)'

            if prefs.get('soundcloud'):
                soundcloud = prefs['soundcloud']
            else:
                soundcloud = 'N/A'

            if prefs.get('bio'):
                bio = prefs['bio']
            else:
                bio = 'N/A'
        else:
            svc = 'N/A (not set)'
            soundcloud = 'N/A'
            bio = 'N/A'

        embed = discord.Embed(
            title=f'{user} ({user.display_name})',
            color=discord.Color(random.randint(0x000000, 0xffffff)),
            timestamp=datetime.datetime.now()
        )
        embed.set_thumbnail(
            url=user.avatar_url
        )
        embed.add_field(
            name=f'One of {user.display_name}\'s favorite songs',
            value=favorite_song_final,
            inline=False
        )
        embed.add_field(
            name=f'Preferred music service',
            value=svc,
            inline=False
        )
        embed.add_field(
            name=f'SoundCloud <:soundcloud:528067302659194880>',
            value=soundcloud,
            inline=False
        )
        embed.add_field(
            name=f'Bio',
            value=bio,
            inline=False
        )
        embed.set_footer(
            text=f"Trackrr Music Search",
            icon_url="https://media.discordapp.net/attachments/452763485743349761/452763575878942720/TrackrrLogo.png"
        )
        await ctx.send(embed=embed)


class DBFunctions:

    def __init__(self, bot):
        self.bot = bot

    @commands.group(name='prefs', invoke_without_command=True)
    @commands.cooldown(3, 5, commands.BucketType.guild)
    @commands.cooldown(1, 5, commands.BucketType.user)
    async def prefs(self, ctx):
        cmdprefix = (await self.bot.command_prefix(self.bot, ctx.message))[-1]
        description = f"""
`{cmdprefix}{ctx.invoked_with} <option> <value>`
Example: `{cmdprefix}{ctx.invoked_with} service spotify`

__**Options:**__

__Guild - {ctx.guild.name}__
prefix - Change Trackrr's prefix for the current guild (`Administrator` only)

__User - {ctx.author}__
service - Add/change your preferred music source. This lets you use search commands without specifying a service.
soundcloud - Add a SoundCloud link to your profile view.
bio - Add a bio to your profile.

        """.strip()
        embed = discord.Embed(title='Trackrr Preferences 🛠', description=description, color=discord.Color(random.randint(0x000000, 0xffffff)))
        embed.set_footer(text="Trackrr Music Search", icon_url="https://media.discordapp.net/attachments/452763485743349761/452763575878942720/TrackrrLogo.png")
        await ctx.send(embed=embed)

    @prefs.command(name='service')
    async def prefs_service(self, ctx, svc=None):
        cmdprefix = (await self.bot.command_prefix(self.bot, ctx.message))[-1]
        if not svc:
            current_service_raw = await db.preferredsvc.find_one({'uid': ctx.author.id})
            current_service = copy.deepcopy(getattr(current_service_raw, 'get', {}.get)('service'))
            if current_service:
                the_emoji = [emoji for emoji in self.bot.support_server.emojis if emoji.name == current_service.lower()]
                if the_emoji:
                    current_service = str(the_emoji[0]) + f' **{current_service}**'
            else:
                current_service = f'❌ No preferred service set up. Try running `{cmdprefix}prefs service <service name>`.'
            embed = discord.Embed(title=f'{ctx.author.display_name} - Preferred Service', description=current_service, timestamp=datetime.datetime.now())
            embed.set_footer(text="Trackrr Music Search", icon_url="https://media.discordapp.net/attachments/452763485743349761/452763575878942720/TrackrrLogo.png")
            return await ctx.send(embed=embed)
        svc = svc.lower()
        services = self.bot.get_cog('SearchSong').services + self.bot.get_cog('SearchAlbum').services
        if svc not in services:
            return
        if not await db.preferredsvc.find_one_and_update({'uid': ctx.author.id}, {'$set': {'service': svc}}):
            await db.preferredsvc.insert_one({'uid': ctx.author.id, 'service': svc})
        await ctx.send(f'✅ Set your preferred service to {svc}')

    @prefs.command(name='bio')
    async def prefs_bio(self, ctx, *, bio=None):
        cmdprefix = (await self.bot.command_prefix(self.bot, ctx.message))[-1]
        if not bio:
            getbioraw = await db.preferredsvc.find_one({'uid': ctx.author.id})
            getbio = copy.deepcopy(getattr(getbioraw, 'get', {}.get)('bio'))
            if getbio:
                pass
            else:
                getbio = f'❌ You do not have a bio! Try running `{cmdprefix}prefs bio <bio>`.'
            embed = discord.Embed(title=f'{ctx.author.display_name} - Profile Bio', description=f'```{getbio}```', timestamp=datetime.datetime.now())
            embed.set_footer(text="Trackrr Music Search", icon_url="https://media.discordapp.net/attachments/452763485743349761/452763575878942720/TrackrrLogo.png")
            return await ctx.send(embed=embed)
        if len(bio) > 150:
            return await ctx.send('❌ Bio too long! Please shorten it to under 150 characters.')
        if not await db.preferredsvc.find_one_and_update({'uid': ctx.author.id}, {'$set': {'bio': bio}}):
            await db.preferredsvc.insert_one({'uid': ctx.author.id, 'bio': bio})
        await ctx.send(f'✅ Set your profile bio to ```{bio}```')

    @prefs.command(name='soundcloud')
    async def prefs_soundcloud(self, ctx, link=None):
        cmdprefix = (await self.bot.command_prefix(self.bot, ctx.message))[-1]
        if not link:
            link_raw = await db.preferredsvc.find_one({'uid': ctx.author.id})
            sc_link = copy.deepcopy(
                getattr(
                    link_raw,
                    'get',
                    {}.get
                )('soundcloud')
            )
            if sc_link:
                sc_link = f'[{sc_link}]({sc_link})'
            else:
                sc_link = f'❌ No SoundCloud set up. Try running `{cmdprefix}prefs soundcloud <link>`.'
            embed = discord.Embed(
                title=f'{ctx.author.display_name} - SoundCloud <:soundcloud:528067302659194880>',
                description=sc_link,
                timestamp=datetime.datetime.now()
            )
            embed.set_footer(
                text=f"Trackrr Music Search | Run '{cmdprefix}prefs soundcloud remove' to unlink your SoundCloud.",
                icon_url="https://media.discordapp.net/attachments/452763485743349761/452763575878942720/TrackrrLogo.png"
            )
            return await ctx.send(embed=embed)
        if link == 'remove' or link == 'delete':
            doc = await db.preferredsvc.find_one({'uid': ctx.author.id})
            if not doc:
                doc = {}
            if doc.get('soundcloud'):
                doc.pop('soundcloud')
                await db.preferredsvc.find_one_and_replace({'uid': ctx.author.id}, doc)
                return await ctx.send('✅ Successfully removed your linked SoundCloud.')
            else:
                return await ctx.send(f'❌ No SoundCloud set up. Try running `{cmdprefix}prefs soundcloud <link>`.')
        link_parsed = urllib.parse.urlparse(link)
        if any([
            not link_parsed.scheme,
            link_parsed.netloc != 'soundcloud.com',
            not link_parsed.path
        ]):
            link = 'https://soundcloud.com/' + link
        if not await db.preferredsvc.find_one_and_update({'uid': ctx.author.id}, {'$set': {'soundcloud': link}}):
            await db.preferredsvc.insert_one({'uid': ctx.author.id, 'soundcloud': link})
        await ctx.send(f'✅ Set your SoundCloud to {link}.\nRun `{cmdprefix}prefs soundcloud remove` to unlink your SoundCloud.')

    @prefs.command(name='prefix')
    @commands.has_permissions(administrator=True)
    async def prefs_prefix(self, ctx, prefix=None):
        cmdprefix = (await self.bot.command_prefix(self.bot, ctx.message))[-1]
        if not prefix:
            if cmdprefix == '^':
                current_prefix = f'❌ This server does not have a custom prefix set up! Try running `{cmdprefix}prefs prefix <prefix>`.'
            else:
                current_prefix = f'This guild\'s current custom prefix is `{cmdprefix}`.'
            embed = discord.Embed(title=f'{ctx.guild.name} - Prefix', description=current_prefix, timestamp=datetime.datetime.now())
            embed.set_footer(text="Trackrr Music Search", icon_url="https://media.discordapp.net/attachments/452763485743349761/452763575878942720/TrackrrLogo.png")
            return await ctx.send(embed=embed)
        if not await db.preferredsvc.find_one_and_update({'gid': ctx.guild.id}, {'$set': {'prefix': prefix}}):
            await db.preferredsvc.insert_one({'gid': ctx.guild.id, 'prefix': prefix})
        await ctx.send(f'✅ Set your guild\'s prefix to {prefix}')


def setup(bot):
    bot.add_cog(DBFunctions(bot))
    bot.add_cog(Profiles(bot))
