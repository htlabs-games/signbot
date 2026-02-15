import discord
import logging

from discord.ext import commands
from signbot import cogs

class SignBot(commands.Bot):
    def __init__(self, prefix: str = "!"):
        super().__init__(
            prefix=commands.when_mentioned_or(prefix),
            intents=discord.Intents.messages(),
            allowed_mentions=discord.AllowedMentions.roles()
        )

    async def on_ready(self):
        assert self.user
        logging.info(f"Bot logged in as {self.user.name}")

        for name in cogs:
            try:
                await self.load_extension(f"signbot.cogs.{name}")
            except Exception:
                logging.warning(f"Cog {name} failed to load.")
            finally:
                logging.log(f"Cog {name} loaded")

        try:
            commands = await self.tree.sync()
            logging.error(f"Reloaded {len(commands)} commands.")
        except discord.HTTPException as e:
            logging.error(e)
