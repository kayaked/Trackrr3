import discord
from discord.ext import commands
import os
from cogs.mods.keys import Keys
import motor.motor_asyncio
client = motor.motor_asyncio.AsyncIOMotorClient()
db=client['Trackrr']

splash = "  " + r"""
  ______                __                %%%%%%%%
 /_  __/________ ______/ /____________  %%%%   %%%%
  / / / ___/ __ `/ ___/ //_/ ___/ ___/  %% / %  %%%
 / / / /  / /_/ / /__/ ,< / /  / /      %%%     $%%
/_/ /_/   \__,_/\___/_/|_/_/  /_/        %%%%%%%%
____________________________________________________

""".strip()

# Don't forget to disable before pushing..
debug_mode = True


async def prefix_func(bot, msg):
    prefixes = [f'<@!{bot.user.id}> ', f'<@{bot.user.id}> ', '^']
    prefix = await db.preferredsvc.find_one({'gid':msg.guild.id})
    if prefix:
        prefixes[-1] = prefix.get('prefix', '^')
    return prefixes

class Reyackrr(commands.Bot):
    def __init__(self):
        self.token = Keys.DISCORDTOKEN
        if debug_mode == True:
            super().__init__(command_prefix="?")
        else:
            super().__init__(command_prefix=prefix_func)
        self.remove_command('help')

    def run(self, token=None):
        if not token: token=self.token
        super().run(self.token)

    async def on_ready(self):
        print(splash)
        for ext in [file[:-3] for file in os.listdir('cogs') if file.endswith('.py') and os.path.isfile(os.path.join('cogs', file))]:
            package = "{prefix}.{package}".format(prefix="cogs", package=ext)
            self.load_extension(package)
            print('Loaded extension {}'.format(package))

Reyackrr().run()