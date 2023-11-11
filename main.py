import os

import discord
from discord.ext import commands

from dotenv import load_dotenv

load_dotenv()


class Krzysv2(commands.Bot):
    def __init__(self):
        super().__init__(command_prefix='!', intents=discord.Intents.all())

    async def setup_hook(self) -> None:
        await self.load_extension('cogs.main_cog')
        await self.load_extension('cogs.ping_cog')
        await self.tree.sync()

    async def on_ready(self) -> None:
        pass


if __name__ == '__main__':
    client = Krzysv2()

    client.run(os.getenv('DISCORD_TOKEN'))
