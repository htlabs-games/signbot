import discord
import logging

from discord.ext import commands
from os import getenv
from signbot import cogs

class SignBot(commands.Bot):
    def __init__(self, prefix: str = "="):
        super().__init__(
            command_prefix=commands.when_mentioned_or(prefix),
            intents=discord.Intents(33281),
            allowed_mentions=discord.AllowedMentions(roles=True, replied_user=False)
        )

        self.owner_ids = [int(x) for x in getenv("OWNER_IDS").split(",")]

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

    async def on_command_error(self, ctx: commands.Context, exception: commands.errors.CommandError):
        if isinstance(exception, (commands.errors.NotOwner, commands.errors.CommandNotFound)):
            return

        if isinstance(exception, commands.errors.MissingRequiredArgument):
            return await ctx.reply(content=
                f"Missing argument for this command: `{exception.param.name}`")