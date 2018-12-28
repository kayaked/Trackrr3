import discord
from discord.ext import commands
import motor.motor_asyncio

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
        if not svc:
            current_service = await db.preferredsvc.find_one({'uid':ctx.author.id})
            await ctx.send(getattr(current_service, 'get', {}.get)('service', f'No preferred service set up. Try running `{self.bot.command_prefix}prefs service <service name>`.'))
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
                return await ctx.send(f'No preferred service set up. Try running `{cmdprefix}prefs prefix <prefix>`.')
            else:
                return await ctx.send(f'This guild\'s current custom prefix is `{cmdprefix}`.')
        if not await db.preferredsvc.find_one_and_update({'gid':ctx.guild.id}, {'$set':{'prefix':prefix}}):
            await db.preferredsvc.insert_one({'gid':ctx.guild.id, 'prefix':prefix})
        await ctx.send(f'Set your guild\'s prefix to {prefix}')

def setup(bot):
    bot.add_cog(DBFunctions(bot))