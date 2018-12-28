import discord
from discord.ext import commands
import os
from cogs.mods.keys import Keys

splash = "  " + r"""
  ______                __                %%%%%%%%
 /_  __/________ ______/ /____________  %%%%   %%%%
  / / / ___/ __ `/ ___/ //_/ ___/ ___/  %% / %  %%%
 / / / /  / /_/ / /__/ ,< / /  / /      %%%     $%%
/_/ /_/   \__,_/\___/_/|_/_/  /_/        %%%%%%%%

""".strip()

class Reyackrr(commands.Bot):
    def __init__(self):
        self.token = Keys.DISCORDTOKEN
        super().__init__(command_prefix="^")
        self.remove_command('help')

    def run(self, token=None):
        if not token: token=self.token
        super().run(self.token)

    async def on_ready(self):
        print(splash)
        for ext in [file[:-3] for file in os.listdir('cogs') if file.endswith('.py') and os.path.isfile(os.path.join('cogs', file))]:
            self.load_extension("{prefix}.{package}".format(prefix="cogs", package=ext))

Reyackrr().run()