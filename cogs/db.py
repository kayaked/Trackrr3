import discord
from discord.ext import commands
import motor.motor_asyncio
import copy
import datetime

client = motor.motor_asyncio.AsyncIOMotorClient()
db = client['Trackrr']

class DBFunctions:

    def __init__(self, bot):
        self.bot=bot
    
    @commands.group(name='prefs', invoke_without_command=True)
    async def prefs(self, ctx):
        await ctx.send(':tools:')
    
    @prefs.command(name='service')
    async def prefs_service(self, ctx, svc=None):
        cmdprefix = (await self.bot.command_prefix(self.bot, ctx.message))[-1]
        if not svc:
            current_service_raw = await db.preferredsvc.find_one({'uid':ctx.author.id})
            current_service = copy.deepcopy(getattr(current_service_raw, 'get', {}.get)('service'))
            if current_service:
                the_emoji = [emoji for emoji in self.bot.emojis if emoji.name == current_service.lower()]
                if the_emoji:
                    current_service = str(the_emoji[0]) + f' **{current_service}**'
            else:
                current_service = f'No preferred service set up. Try running `{cmdprefix}prefs service <service name>`.'
            embed = discord.Embed(title=f'{ctx.author.display_name} - Preferred Service', description=current_service, timestamp=datetime.datetime.now())
            embed.set_footer(text="Trackrr Music Search", icon_url="https://media.discordapp.net/attachments/452763485743349761/452763575878942720/TrackrrLogo.png")
            await ctx.send(embed=embed)
        services = self.bot.get_cog('SearchSong').services + self.bot.get_cog('SearchAlbum').services
        if svc not in services:
            return
        if not await db.preferredsvc.find_one_and_update({'uid':ctx.author.id}, {'$set':{'service':svc}}):
            await db.preferredsvc.insert_one({'uid':ctx.author.id, 'service':svc})
        await ctx.send(f'Set your preferred service to {svc}')

    @prefs.command(name='prefix')
    @commands.has_permissions(administrator=True)
    async def prefs_prefix(self, ctx, prefix=None):
        cmdprefix = (await self.bot.command_prefix(self.bot, ctx.message))[-1]
        if not prefix:
            if cmdprefix == '^':
                current_prefix = f'This server does not have a custom prefix set up! Try running `{cmdprefix}prefs prefix <prefix>`.'
            else:
                current_prefix = f'This guild\'s current custom prefix is `{cmdprefix}`.'
            embed = discord.Embed(title=f'{ctx.guild.name} - Prefix', description=current_prefix, timestamp=datetime.datetime.now())
            embed.set_footer(text="Trackrr Music Search", icon_url="https://media.discordapp.net/attachments/452763485743349761/452763575878942720/TrackrrLogo.png")
            return await ctx.send(embed=embed)
        if not await db.preferredsvc.find_one_and_update({'gid':ctx.guild.id}, {'$set':{'prefix':prefix}}):
            await db.preferredsvc.insert_one({'gid':ctx.guild.id, 'prefix':prefix})
        await ctx.send(f'Set your guild\'s prefix to {prefix}')

def setup(bot):
    bot.add_cog(DBFunctions(bot))