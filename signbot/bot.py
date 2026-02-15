import discord
import logging

from discord.ext import commands
from signbot import cogs

class SignBot(commands.Bot):
    def __init__(self, prefix: str = "!"):
        super().__init__(
            command_prefix=commands.when_mentioned_or(prefix),
            intents=discord.Intents(32768),
            allowed_mentions=discord.AllowedMentions(roles=True, replied_user=False)
        )

    async def on_ready(self):
        assert self.user
        logging.info(f"Bot logged in as {self.user.name}")

        for name in cogs:
            try:
                await self.load_extension(f"signbot.cogs.{name}")
            except Exception as e:
                logging.warning(f"Cog {name} failed to load.")
            finally:
                logging.info(f"Cog {name} loaded")
