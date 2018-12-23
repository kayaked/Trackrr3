import discord
from discord.ext import commands
import os

class Reyackrr(commands.Bot):
    def __init__(self):
        self.token = "NDU3NjU0NjI4MzQzODczNTM3.Dv2UIA.PXz8TE1QqcGDj1gOu0a0_tMpAT8"
        super().__init__(command_prefix="!!")

    def run(self, token=None):
        if not token: token=self.token
        super().run(self.token)

    async def on_ready(self):
        print("Reyackrr")
        yakrrcogs = [
            'user'
        ]
        for ext in [file[:-3] for file in os.listdir('cogs') if file.endswith('.py') and os.path.isfile(os.path.join('cogs', file))]:
            self.load_extension("{prefix}.{package}".format(prefix="cogs", package=ext))

Reyackrr().run()