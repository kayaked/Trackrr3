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
        if not await db.preferredsvc.find_one_and_replace({'uid':ctx.author.id}, {'uid':ctx.author.id, 'service':svc}):
            await db.preferredsvc.insert_one({'uid':ctx.author.id, 'service':svc})
        await ctx.send(f'Set your preferred service to {svc}')

def setup(bot):
    bot.add_cog(DBFunctions(bot))